package repository

import (
	"rss-knowledge-base/internal/model"

	"gorm.io/gorm"
)

type CategoryRepository struct {
	db *gorm.DB
}

func NewCategoryRepository() *CategoryRepository {
	return &CategoryRepository{db: model.DB}
}

func (r *CategoryRepository) Create(category *model.Category) error {
	return r.db.Create(category).Error
}

func (r *CategoryRepository) GetByID(id int64) (*model.Category, error) {
	var category model.Category
	err := r.db.First(&category, id).Error
	if err != nil {
		return nil, err
	}
	return &category, nil
}

func (r *CategoryRepository) GetAll() ([]model.Category, error) {
	var categories []model.Category
	err := r.db.Order("sort_order ASC, created_at DESC").Find(&categories).Error
	return categories, err
}

func (r *CategoryRepository) Update(category *model.Category) error {
	return r.db.Save(category).Error
}

func (r *CategoryRepository) Delete(id int64) error {
	return r.db.Delete(&model.Category{}, id).Error
}

func (r *CategoryRepository) UpdateOrder(categories []model.Category) error {
	for _, cat := range categories {
		if err := r.db.Model(&cat).Update("sort_order", cat.SortOrder).Error; err != nil {
			return err
		}
	}
	return nil
}
