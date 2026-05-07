package service

import (
	"errors"

	"rss-knowledge-base/internal/model"
	"rss-knowledge-base/internal/repository"
)

type TagService struct {
	tagRepo *repository.TagRepository
}

func NewTagService() *TagService {
	return &TagService{
		tagRepo: repository.NewTagRepository(),
	}
}

func (s *TagService) CreateTag(tag *model.Tag) error {
	if tag.Name == "" {
		return errors.New("name is required")
	}
	return s.tagRepo.Create(tag)
}

func (s *TagService) GetTag(id int64) (*model.Tag, error) {
	return s.tagRepo.GetByID(id)
}

func (s *TagService) GetAllTags() ([]model.Tag, error) {
	return s.tagRepo.GetAll()
}

func (s *TagService) UpdateTag(tag *model.Tag) error {
	return s.tagRepo.Update(tag)
}

func (s *TagService) DeleteTag(id int64) error {
	return s.tagRepo.Delete(id)
}

func (s *TagService) AddArticleTag(articleID, tagID int64) error {
	return s.tagRepo.AddArticleTag(articleID, tagID)
}

func (s *TagService) RemoveArticleTag(articleID, tagID int64) error {
	return s.tagRepo.RemoveArticleTag(articleID, tagID)
}
