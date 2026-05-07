package service

import (
	"errors"
	"rss-knowledge-base/internal/model"
	"rss-knowledge-base/internal/repository"
)

type CategoryService struct {
	categoryRepo *repository.CategoryRepository
}

func NewCategoryService() *CategoryService {
	return &CategoryService{
		categoryRepo: repository.NewCategoryRepository(),
	}
}

func (s *CategoryService) CreateCategory(category *model.Category) error {
	if category.Name == "" {
		return errors.New("name is required")
	}
	return s.categoryRepo.Create(category)
}

func (s *CategoryService) GetCategory(id int64) (*model.Category, error) {
	return s.categoryRepo.GetByID(id)
}

func (s *CategoryService) GetAllCategories() ([]model.Category, error) {
	return s.categoryRepo.GetAll()
}

func (s *CategoryService) UpdateCategory(category *model.Category) error {
	return s.categoryRepo.Update(category)
}

func (s *CategoryService) DeleteCategory(id int64) error {
	return s.categoryRepo.Delete(id)
}

func (s *CategoryService) UpdateOrder(categories []model.Category) error {
	return s.categoryRepo.UpdateOrder(categories)
}
