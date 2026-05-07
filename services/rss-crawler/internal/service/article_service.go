package service

import (
	"rss-knowledge-base/internal/model"
	"rss-knowledge-base/internal/repository"
)

type ArticleService struct {
	articleRepo *repository.ArticleRepository
}

func NewArticleService() *ArticleService {
	return &ArticleService{
		articleRepo: repository.NewArticleRepository(),
	}
}

func (s *ArticleService) GetArticle(id int64) (*model.Article, error) {
	return s.articleRepo.GetByID(id)
}

func (s *ArticleService) GetArticles(filter repository.ArticleFilter) ([]model.Article, int64, error) {
	return s.articleRepo.GetList(filter)
}

func (s *ArticleService) MarkAsRead(id int64) error {
	return s.articleRepo.MarkAsRead(id)
}

func (s *ArticleService) MarkAllAsRead() error {
	return s.articleRepo.MarkAllAsRead()
}

func (s *ArticleService) DeleteArticle(id int64) error {
	return s.articleRepo.Delete(id)
}

func (s *ArticleService) GetUnanalyzedArticles() ([]model.Article, error) {
	return s.articleRepo.GetUnanalyzed()
}
