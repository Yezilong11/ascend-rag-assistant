package handler

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"rss-knowledge-base/internal/repository"
	"rss-knowledge-base/internal/service"
)

type ArticleHandler struct {
	articleService *service.ArticleService
}

func NewArticleHandler() *ArticleHandler {
	return &ArticleHandler{
		articleService: service.NewArticleService(),
	}
}

func (h *ArticleHandler) RegisterRoutes(r *gin.RouterGroup) {
	articles := r.Group("/articles")
	{
		articles.GET("", h.List)
		articles.GET("/:id", h.Get)
		articles.PUT("/:id/read", h.MarkRead)
		articles.PUT("/read-all", h.MarkAllRead)
		articles.DELETE("/:id", h.Delete)
	}
}

func (h *ArticleHandler) List(c *gin.Context) {
	filter := repository.ArticleFilter{
		Page:  1,
		Limit: 20,
	}

	if page := c.Query("page"); page != "" {
		if p, err := strconv.Atoi(page); err == nil {
			filter.Page = p
		}
	}
	if limit := c.Query("limit"); limit != "" {
		if l, err := strconv.Atoi(limit); err == nil {
			filter.Limit = l
		}
	}
	if feedID := c.Query("feed_id"); feedID != "" {
		if id, err := strconv.ParseInt(feedID, 10, 64); err == nil {
			filter.FeedID = &id
		}
	}
	if categoryID := c.Query("category_id"); categoryID != "" {
		if id, err := strconv.ParseInt(categoryID, 10, 64); err == nil {
			filter.CategoryID = &id
		}
	}
	if readStatus := c.Query("read_status"); readStatus != "" {
		if status, err := strconv.Atoi(readStatus); err == nil {
			filter.ReadStatus = &status
		}
	}

	articles, total, err := h.articleService.GetArticles(filter)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"data": articles, "total": total})
}

func (h *ArticleHandler) Get(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}

	article, err := h.articleService.GetArticle(id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "article not found"})
		return
	}
	c.JSON(http.StatusOK, article)
}

func (h *ArticleHandler) MarkRead(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}

	if err := h.articleService.MarkAsRead(id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "marked as read"})
}

func (h *ArticleHandler) MarkAllRead(c *gin.Context) {
	if err := h.articleService.MarkAllAsRead(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "all marked as read"})
}

func (h *ArticleHandler) Delete(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}

	if err := h.articleService.DeleteArticle(id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "deleted"})
}
