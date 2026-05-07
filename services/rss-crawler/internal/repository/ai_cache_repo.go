package repository

import (
	"rss-knowledge-base/internal/model"

	"gorm.io/gorm"
)

type AICacheRepository struct {
	db *gorm.DB
}

func NewAICacheRepository() *AICacheRepository {
	return &AICacheRepository{db: model.DB}
}

func (r *AICacheRepository) Create(cache *model.AIAnalysisCache) error {
	return r.db.Create(cache).Error
}

func (r *AICacheRepository) GetByHash(hash string) (*model.AIAnalysisCache, error) {
	var cache model.AIAnalysisCache
	err := r.db.Where("content_hash = ?", hash).First(&cache).Error
	if err != nil {
		return nil, err
	}
	return &cache, nil
}

func (r *AICacheRepository) Update(cache *model.AIAnalysisCache) error {
	return r.db.Save(cache).Error
}
