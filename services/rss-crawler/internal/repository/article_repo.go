package repository

import (
	"rss-knowledge-base/internal/model"

	"gorm.io/gorm"
)

type ArticleRepository struct {
	db *gorm.DB
}

func NewArticleRepository() *ArticleRepository {
	return &ArticleRepository{db: model.DB}
}

func (r *ArticleRepository) Create(article *model.Article) error {
	return r.db.Create(article).Error
}

func (r *ArticleRepository) CreateBatch(articles []model.Article) error {
	return r.db.CreateInBatches(articles, 100).Error
}

func (r *ArticleRepository) GetByID(id int64) (*model.Article, error) {
	var article model.Article
	err := r.db.Preload("Feed").Preload("Tags").First(&article, id).Error
	if err != nil {
		return nil, err
	}
	return &article, nil
}

func (r *ArticleRepository) GetByHash(hash string) (*model.Article, error) {
	var article model.Article
	err := r.db.Where("content_hash = ?", hash).First(&article).Error
	if err != nil {
		return nil, err
	}
	return &article, nil
}

func (r *ArticleRepository) GetList(filter ArticleFilter) ([]model.Article, int64, error) {
	var articles []model.Article
	var total int64

	query := r.db.Model(&model.Article{})

	if filter.FeedID != nil {
		query = query.Where("feed_id = ?", *filter.FeedID)
	}
	if filter.CategoryID != nil {
		query = query.Joins("JOIN feeds ON articles.feed_id = feeds.id").
			Where("feeds.category_id = ?", *filter.CategoryID)
	}
	if filter.ReadStatus != nil {
		query = query.Where("read_status = ?", *filter.ReadStatus)
	}

	query.Count(&total)

	if filter.Limit != 0 {
		query = query.Offset((filter.Page - 1) * filter.Limit).Limit(filter.Limit)
	}

	query = query.Preload("Feed").Preload("Tags").Order("published_at DESC")

	err := query.Find(&articles).Error
	return articles, total, err
}

func (r *ArticleRepository) MarkAsRead(id int64) error {
	return r.db.Model(&model.Article{}).Where("id = ?", id).Update("read_status", 1).Error
}

func (r *ArticleRepository) MarkAllAsRead() error {
	return r.db.Model(&model.Article{}).Where("read_status = ?", 0).Update("read_status", 1).Error
}

func (r *ArticleRepository) Delete(id int64) error {
	return r.db.Delete(&model.Article{}, id).Error
}

func (r *ArticleRepository) GetUnanalyzed() ([]model.Article, error) {
	var articles []model.Article
	err := r.db.Where("summary IS NULL OR summary = ''").Limit(100).Find(&articles).Error
	return articles, err
}

func (r *ArticleRepository) Update(article *model.Article) error {
	return r.db.Save(article).Error
}

type ArticleFilter struct {
	FeedID      *int64
	CategoryID  *int64
	TagID       *int64
	ReadStatus  *int
	Keyword     string
	Page        int
	Limit       int
}
