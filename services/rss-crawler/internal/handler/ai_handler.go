package handler

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"rss-knowledge-base/internal/config"
	"rss-knowledge-base/internal/repository"
	"rss-knowledge-base/internal/service"
)

type AIHandler struct {
	aiService     *service.AIService
	articleRepo   *repository.ArticleRepository
	articleSvc    *service.ArticleService
	configPath    string
}

func NewAIHandler(cfg *config.Config) *AIHandler {
	return &AIHandler{
		aiService:   service.NewAIService(cfg),
		articleRepo: repository.NewArticleRepository(),
		articleSvc:  service.NewArticleService(),
		configPath:  "config.yaml",
	}
}

func (h *AIHandler) RegisterRoutes(r *gin.RouterGroup) {
	ai := r.Group("/ai")
	{
		ai.GET("/config", h.GetConfig)
		ai.PUT("/config", h.UpdateConfig)
		ai.POST("/test", h.TestConnection)
	}

	articles := r.Group("/articles")
	{
		articles.POST("/:id/analyze", h.AnalyzeArticle)
		articles.POST("/analyze-all", h.AnalyzeAll)
	}
}

type AIConfig struct {
	Host    string `json:"host"`
	Model   string `json:"model"`
	Timeout int    `json:"timeout"`
	Enabled bool   `json:"enabled"`
}

func (h *AIHandler) GetConfig(c *gin.Context) {
	cfg, err := config.Load("config.yaml")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"host":    cfg.Ollama.Host,
		"model":   cfg.Ollama.Model,
		"timeout": cfg.Ollama.Timeout,
		"enabled": cfg.AI.Enabled,
	})
}

func (h *AIHandler) UpdateConfig(c *gin.Context) {
	var cfg AIConfig
	if err := c.ShouldBindJSON(&cfg); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	cfgObj, err := config.Load("config.yaml")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	cfgObj.Ollama.Host = cfg.Host
	cfgObj.Ollama.Model = cfg.Model
	cfgObj.Ollama.Timeout = cfg.Timeout
	cfgObj.AI.Enabled = cfg.Enabled

	if err := config.Save("config.yaml", cfgObj); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "config updated"})
}

func (h *AIHandler) TestConnection(c *gin.Context) {
	cfg, err := config.Load("config.yaml")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	testService := service.NewAIService(cfg)
	result, err := testService.TestOllama()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": result,
	})
}

func (h *AIHandler) AnalyzeArticle(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}

	article, err := h.articleSvc.GetArticle(id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "article not found"})
		return
	}

	analysis, err := h.aiService.AnalyzeArticle(article)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"summary":   analysis.Summary,
		"keywords":  analysis.Keywords,
		"sentiment": analysis.Sentiment,
	})
}

func (h *AIHandler) AnalyzeAll(c *gin.Context) {
	articles, err := h.articleSvc.GetUnanalyzedArticles()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	go func() {
		for _, article := range articles {
			h.aiService.AnalyzeArticle(&article)
		}
	}()

	c.JSON(http.StatusOK, gin.H{"message": "analysis started", "count": len(articles)})
}