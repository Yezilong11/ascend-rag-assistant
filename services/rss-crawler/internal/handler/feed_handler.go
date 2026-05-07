package handler

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"rss-knowledge-base/internal/model"
	"rss-knowledge-base/internal/service"
)

type FeedHandler struct {
	feedService  *service.FeedService
	crawlService *service.CrawlService
}

func NewFeedHandler(crawlSvc *service.CrawlService) *FeedHandler {
	return &FeedHandler{
		feedService:  service.NewFeedService(),
		crawlService: crawlSvc,
	}
}

func (h *FeedHandler) RegisterRoutes(r *gin.RouterGroup) {
	feeds := r.Group("/feeds")
	{
		feeds.GET("", h.List)
		feeds.GET("/:id", h.Get)
		feeds.POST("", h.Create)
		feeds.PUT("/:id", h.Update)
		feeds.DELETE("/:id", h.Delete)
		feeds.POST("/:id/crawl", h.Crawl)
		feeds.POST("/crawl-all", h.CrawlAll)
	}
}

func (h *FeedHandler) List(c *gin.Context) {
	feeds, err := h.feedService.GetAllFeeds()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, feeds)
}

func (h *FeedHandler) Get(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}

	feed, err := h.feedService.GetFeed(id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "feed not found"})
		return
	}
	c.JSON(http.StatusOK, feed)
}

func (h *FeedHandler) Create(c *gin.Context) {
	var feed model.Feed
	if err := c.ShouldBindJSON(&feed); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.feedService.CreateFeed(&feed); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusCreated, feed)
}

func (h *FeedHandler) Update(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}

	var feed model.Feed
	if err := c.ShouldBindJSON(&feed); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	feed.ID = id
	if err := h.feedService.UpdateFeed(&feed); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, feed)
}

func (h *FeedHandler) Delete(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}

	if err := h.feedService.DeleteFeed(id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "deleted"})
}

func (h *FeedHandler) Crawl(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}

	if err := h.crawlService.CrawlFeedByID(id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "crawl started"})
}

func (h *FeedHandler) CrawlAll(c *gin.Context) {
	h.crawlService.CrawlAll()
	c.JSON(http.StatusOK, gin.H{"message": "crawl all started"})
}
