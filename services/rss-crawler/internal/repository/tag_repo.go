package repository

import (
	"rss-knowledge-base/internal/model"

	"gorm.io/gorm"
)

type TagRepository struct {
	db *gorm.DB
}

func NewTagRepository() *TagRepository {
	return &TagRepository{db: model.DB}
}

func (r *TagRepository) Create(tag *model.Tag) error {
	return r.db.Create(tag).Error
}

func (r *TagRepository) GetByID(id int64) (*model.Tag, error) {
	var tag model.Tag
	err := r.db.First(&tag, id).Error
	if err != nil {
		return nil, err
	}
	return &tag, nil
}

func (r *TagRepository) GetAll() ([]model.Tag, error) {
	var tags []model.Tag
	err := r.db.Order("created_at DESC").Find(&tags).Error
	return tags, err
}

func (r *TagRepository) GetByName(name string) (*model.Tag, error) {
	var tag model.Tag
	err := r.db.Where("name = ?", name).First(&tag).Error
	if err != nil {
		return nil, err
	}
	return &tag, nil
}

func (r *TagRepository) Update(tag *model.Tag) error {
	return r.db.Save(tag).Error
}

func (r *TagRepository) Delete(id int64) error {
	return r.db.Delete(&model.Tag{}, id).Error
}

func (r *TagRepository) AddArticleTag(articleID, tagID int64) error {
	return r.db.Exec("INSERT INTO article_tags (article_id, tag_id) VALUES (?, ?)", articleID, tagID).Error
}

func (r *TagRepository) RemoveArticleTag(articleID, tagID int64) error {
	return r.db.Exec("DELETE FROM article_tags WHERE article_id = ? AND tag_id = ?", articleID, tagID).Error
}
