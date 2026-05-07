package repository

import (
	"time"

	"rss-knowledge-base/internal/model"

	"gorm.io/gorm"
)

type FeedRepository struct {
	db *gorm.DB
}

func NewFeedRepository() *FeedRepository {
	return &FeedRepository{db: model.DB}
}

func (r *FeedRepository) Create(feed *model.Feed) error {
	return r.db.Create(feed).Error
}

func (r *FeedRepository) GetByID(id int64) (*model.Feed, error) {
	var feed model.Feed
	err := r.db.Preload("Category").First(&feed, id).Error
	if err != nil {
		return nil, err
	}
	return &feed, nil
}

func (r *FeedRepository) GetAll() ([]model.Feed, error) {
	var feeds []model.Feed
	err := r.db.Preload("Category").Order("created_at DESC").Find(&feeds).Error
	return feeds, err
}

func (r *FeedRepository) GetActiveFeeds() ([]model.Feed, error) {
	var feeds []model.Feed
	err := r.db.Where("status = ?", "active").Find(&feeds).Error
	return feeds, err
}

func (r *FeedRepository) Update(feed *model.Feed) error {
	return r.db.Save(feed).Error
}

func (r *FeedRepository) Delete(id int64) error {
	return r.db.Delete(&model.Feed{}, id).Error
}

func (r *FeedRepository) GetByURL(url string) (*model.Feed, error) {
	var feed model.Feed
	err := r.db.Where("url = ?", url).First(&feed).Error
	if err != nil {
		return nil, err
	}
	return &feed, nil
}

func (r *FeedRepository) UpdateFeedStatus(id int64, status string, errorMsg string) error {
	updates := map[string]interface{}{
		"status": status,
	}
	if errorMsg != "" {
		updates["error_message"] = errorMsg
	}
	return r.db.Model(&model.Feed{}).Where("id = ?", id).Updates(updates).Error
}

func (r *FeedRepository) UpdateCrawlTime(id int64) error {
	now := time.Now()
	nextCrawl := now.Add(time.Duration(60) * time.Minute)
	return r.db.Model(&model.Feed{}).Where("id = ?", id).Updates(map[string]interface{}{
		"last_crawl":  now,
		"next_crawl":  nextCrawl,
		"status":      "active",
	}).Error
}
