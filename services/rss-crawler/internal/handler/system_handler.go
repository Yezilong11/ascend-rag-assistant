package handler

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"rss-knowledge-base/internal/model"
)

type SystemHandler struct {
	startTime time.Time
}

func NewSystemHandler() *SystemHandler {
	return &SystemHandler{
		startTime: time.Now(),
	}
}

func (h *SystemHandler) RegisterRoutes(r *gin.RouterGroup) {
	system := r.Group("/system")
	{
		system.GET("/status", h.Status)
		system.GET("/stats", h.Stats)
	}
}

func (h *SystemHandler) Status(c *gin.Context) {
	status := "healthy"
	databaseStatus := "connected"

	if model.DB == nil {
		status = "unhealthy"
		databaseStatus = "disconnected"
	}

	c.JSON(http.StatusOK, gin.H{
		"status":     status,
		"version":   "1.0.0",
		"uptime":     int(time.Since(h.startTime).Seconds()),
		"database":   databaseStatus,
	})
}

func (h *SystemHandler) Stats(c *gin.Context) {
	var feedsCount int64
	var articlesCount int64
	var categoriesCount int64
	var tagsCount int64
	var unreadCount int64

	if model.DB != nil {
		model.DB.Model(&model.Feed{}).Count(&feedsCount)
		model.DB.Model(&model.Article{}).Count(&articlesCount)
		model.DB.Model(&model.Category{}).Count(&categoriesCount)
		model.DB.Model(&model.Tag{}).Count(&tagsCount)
		model.DB.Model(&model.Article{}).Where("read_status = ?", 0).Count(&unreadCount)
	}

	c.JSON(http.StatusOK, gin.H{
		"feeds_count":      feedsCount,
		"articles_count":   articlesCount,
		"today_articles":   0,
		"categories_count": categoriesCount,
		"tags_count":       tagsCount,
		"unread_count":     unreadCount,
	})
}
