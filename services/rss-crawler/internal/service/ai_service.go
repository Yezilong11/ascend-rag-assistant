package service

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"rss-knowledge-base/internal/config"
	"rss-knowledge-base/internal/model"
	"rss-knowledge-base/internal/repository"
)

type AIService struct {
	config      *config.Config
	articleRepo *repository.ArticleRepository
	cacheRepo   *repository.AICacheRepository
	client      *http.Client
}

func NewAIService(cfg *config.Config) *AIService {
	return &AIService{
		config:      cfg,
		articleRepo: repository.NewArticleRepository(),
		cacheRepo:   repository.NewAICacheRepository(),
		client: &http.Client{
			Timeout: time.Duration(cfg.Ollama.Timeout) * time.Second,
		},
	}
}

type OllamaRequest struct {
	Model  string `json:"model"`
	Prompt string `json:"prompt"`
	Stream bool   `json:"stream"`
}

type OllamaResponse struct {
	Response string `json:"response"`
}

func (s *AIService) AnalyzeArticle(article *model.Article) (*model.AIAnalysisCache, error) {
	cached, err := s.cacheRepo.GetByHash(article.ContentHash)
	if err == nil && cached != nil {
		return cached, nil
	}

	summary, err := s.generateSummary(article.Content)
	if err != nil {
		return nil, fmt.Errorf("failed to generate summary: %w", err)
	}

	keywords, err := s.extractKeywords(article.Content)
	if err != nil {
		log.Printf("Failed to extract keywords: %v", err)
	}

	sentiment, err := s.analyzeSentiment(article.Content)
	if err != nil {
		log.Printf("Failed to analyze sentiment: %v", err)
	}

	analysis := &model.AIAnalysisCache{
		ContentHash: article.ContentHash,
		Summary:     summary,
		Keywords:    keywords,
		Sentiment:   sentiment,
		CreatedAt:   time.Now(),
	}

	if err := s.cacheRepo.Create(analysis); err != nil {
		log.Printf("Failed to cache analysis: %v", err)
	}

	return analysis, nil
}

func (s *AIService) generateSummary(content string) (string, error) {
	prompt := fmt.Sprintf(`请为以下文章生成一个简洁的中文摘要（100字以内）：

%s

摘要：`, content[min(len(content), 2000)])

	return s.callOllama(prompt)
}

func (s *AIService) extractKeywords(content string) (string, error) {
	prompt := fmt.Sprintf(`请从以下文章中提取5个关键词，用逗号分隔：

%s

关键词：`, content[min(len(content), 2000)])

	keywords, err := s.callOllama(prompt)
	if err != nil {
		return "", err
	}

	return fmt.Sprintf(`["%s"]`, keywords), nil
}

func (s *AIService) analyzeSentiment(content string) (string, error) {
	prompt := fmt.Sprintf(`请分析以下文章的情感倾向，只能回答：正面、中性或负面

%s

情感：`, content[min(len(content), 2000)])

	sentiment, err := s.callOllama(prompt)
	if err != nil {
		return "中性", err
	}

	switch sentiment {
	case "正面", "positive", "Positive":
		return "正面", nil
	case "负面", "negative", "Negative":
		return "负面", nil
	default:
		return "中性", nil
	}
}

func (s *AIService) callOllama(prompt string) (string, error) {
	reqBody := OllamaRequest{
		Model:  s.config.Ollama.Model,
		Prompt: prompt,
		Stream: false,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}

	url := fmt.Sprintf("%s/api/generate", s.config.Ollama.Host)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}

	req.Header.Set("Content-Type", "application/json")

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(s.config.Ollama.Timeout)*time.Second)
	defer cancel()

	req = req.WithContext(ctx)

	resp, err := s.client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var result OllamaResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	return result.Response, nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func (s *AIService) TestOllama() (string, error) {
	prompt := "请回复：连接成功"
	return s.callOllama(prompt)
}
