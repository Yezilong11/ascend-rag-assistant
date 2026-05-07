package service

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/mmcdole/gofeed"
	"rss-knowledge-base/internal/config"
	"rss-knowledge-base/internal/model"
	"rss-knowledge-base/internal/repository"
)

type CrawlService struct {
	feedRepo    *repository.FeedRepository
	articleRepo *repository.ArticleRepository
	config      *config.Config
	fp          *gofeed.Parser
	crawlQueue  chan *model.Feed
	wg          sync.WaitGroup
	ctx         context.Context
	cancel      context.CancelFunc
}

func NewCrawlService(cfg *config.Config) *CrawlService {
	ctx, cancel := context.WithCancel(context.Background())
	return &CrawlService{
		feedRepo:    repository.NewFeedRepository(),
		articleRepo: repository.NewArticleRepository(),
		config:      cfg,
		fp:          gofeed.NewParser(),
		crawlQueue:  make(chan *model.Feed, 100),
		ctx:         ctx,
		cancel:      cancel,
	}
}

func (s *CrawlService) Start() {
	log.Println("Crawl service started")
	for i := 0; i < s.config.Crawler.Concurrent; i++ {
		s.wg.Add(1)
		go s.worker(i)
	}
	go s.scheduler()
}

func (s *CrawlService) Stop() {
	log.Println("Crawl service stopping...")
	s.cancel()
	s.wg.Wait()
	close(s.crawlQueue)
	log.Println("Crawl service stopped")
}

func (s *CrawlService) worker(id int) {
	defer s.wg.Done()
	for {
		select {
		case <-s.ctx.Done():
			return
		case feed, ok := <-s.crawlQueue:
			if !ok {
				return
			}
			s.crawlFeed(feed)
		}
	}
}

func (s *CrawlService) scheduler() {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-s.ctx.Done():
			return
		case <-ticker.C:
			s.checkAndCrawl()
		}
	}
}

func (s *CrawlService) checkAndCrawl() {
	feeds, err := s.feedRepo.GetActiveFeeds()
	if err != nil {
		log.Printf("Failed to get active feeds: %v", err)
		return
	}

	now := time.Now()
	for _, feed := range feeds {
		if feed.NextCrawl != nil && feed.NextCrawl.Before(now) {
			select {
			case s.crawlQueue <- &feed:
			default:
				log.Printf("Crawl queue full, skipping feed: %s", feed.Name)
			}
		}
	}
}

func (s *CrawlService) CrawlFeedByID(id int64) error {
	feed, err := s.feedRepo.GetByID(id)
	if err != nil {
		return fmt.Errorf("failed to get feed: %w", err)
	}
	if err := s.crawlFeed(feed); err != nil {
		return err
	}
	return nil
}

func (s *CrawlService) CrawlAll() {
	feeds, err := s.feedRepo.GetActiveFeeds()
	if err != nil {
		log.Printf("Failed to get feeds: %v", err)
		return
	}

	for _, feed := range feeds {
		select {
		case s.crawlQueue <- &feed:
		default:
		}
	}
}

func (s *CrawlService) crawlFeed(feed *model.Feed) error {
	log.Printf("Crawling feed: %s (%s)", feed.Name, feed.URL)

	ctx, cancel := context.WithTimeout(s.ctx, time.Duration(s.config.Crawler.Timeout)*time.Second)
	defer cancel()

	items, err := s.fetchFeed(ctx, feed.URL)
	if err != nil {
		log.Printf("Failed to crawl %s: %v", feed.Name, err)
		s.feedRepo.UpdateFeedStatus(feed.ID, "error", err.Error())
		return err
	}

	var articles []model.Article
	for _, item := range items {
		article := s.parseItem(item, feed.ID)
		if article == nil {
			continue
		}

		existing, _ := s.articleRepo.GetByHash(article.ContentHash)
		if existing != nil {
			continue
		}
		articles = append(articles, *article)
	}

	if len(articles) > 0 {
		if err := s.articleRepo.CreateBatch(articles); err != nil {
			log.Printf("Failed to save articles for %s: %v", feed.Name, err)
			return err
		}
		log.Printf("Saved %d new articles from %s", len(articles), feed.Name)
	}

	s.feedRepo.UpdateCrawlTime(feed.ID)
	s.feedRepo.UpdateFeedStatus(feed.ID, "active", "")
	return nil
}

func (s *CrawlService) fetchFeed(ctx context.Context, url string) ([]*gofeed.Item, error) {
	s.fp.UserAgent = s.config.Crawler.UserAgent
	feed, err := s.fp.ParseURLWithContext(url, ctx)
	if err != nil {
		return nil, err
	}
	return feed.Items, nil
}

func (s *CrawlService) parseItem(item *gofeed.Item, feedID int64) *model.Article {
	if item.Title == "" && item.Link == "" {
		return nil
	}

	content := item.Content
	if content == "" {
		content = item.Description
	}

	hash := s.calculateHash(content + item.Link)

	published := time.Now()
	if item.Published != "" {
		if parsedTime, err := time.Parse(time.RFC1123, item.Published); err == nil {
			published = parsedTime
		} else if parsedTime, err := time.Parse(time.RFC1123Z, item.Published); err == nil {
			published = parsedTime
		} else if parsedTime, err := time.Parse("2006-01-02T15:04:05Z07:00", item.Published); err == nil {
			published = parsedTime
		}
	}

	return &model.Article{
		FeedID:      feedID,
		Title:       item.Title,
		Link:        item.Link,
		Content:     content,
		ContentHash: hash,
		Author:      item.Author.Name,
		PublishedAt: &published,
		CrawledAt:   &published,
		ReadStatus:  0,
	}
}

func (s *CrawlService) calculateHash(content string) string {
	hash := sha256.Sum256([]byte(content))
	return hex.EncodeToString(hash[:])
}
