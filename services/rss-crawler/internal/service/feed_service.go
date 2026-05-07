package service

import (
	"errors"
	"time"

	"rss-knowledge-base/internal/model"
	"rss-knowledge-base/internal/repository"
)

type FeedService struct {
	feedRepo *repository.FeedRepository
}

func NewFeedService() *FeedService {
	return &FeedService{
		feedRepo: repository.NewFeedRepository(),
	}
}

func (s *FeedService) CreateFeed(feed *model.Feed) error {
	if feed.Name == "" || feed.URL == "" {
		return errors.New("name and url are required")
	}
	if feed.CrawlInterval <= 0 {
		feed.CrawlInterval = 60
	}
	feed.Status = "active"
	return s.feedRepo.Create(feed)
}

func (s *FeedService) GetFeed(id int64) (*model.Feed, error) {
	return s.feedRepo.GetByID(id)
}

func (s *FeedService) GetAllFeeds() ([]model.Feed, error) {
	return s.feedRepo.GetAll()
}

func (s *FeedService) GetActiveFeeds() ([]model.Feed, error) {
	return s.feedRepo.GetActiveFeeds()
}

func (s *FeedService) UpdateFeed(feed *model.Feed) error {
	return s.feedRepo.Update(feed)
}

func (s *FeedService) DeleteFeed(id int64) error {
	return s.feedRepo.Delete(id)
}

func (s *FeedService) UpdateFeedStatus(id int64, status string, errorMsg string) error {
	feed, err := s.feedRepo.GetByID(id)
	if err != nil {
		return err
	}
	feed.Status = status
	feed.ErrorMessage = errorMsg
	return s.feedRepo.Update(feed)
}

func (s *FeedService) UpdateCrawlTime(id int64) error {
	feed, err := s.feedRepo.GetByID(id)
	if err != nil {
		return err
	}
	now := time.Now()
	feed.LastCrawl = &now
	nextCrawl := now.Add(time.Duration(feed.CrawlInterval) * time.Minute)
	feed.NextCrawl = &nextCrawl
	return s.feedRepo.Update(feed)
}
