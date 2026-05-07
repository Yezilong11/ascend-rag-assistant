package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/gin-gonic/gin"
	"rss-knowledge-base/internal/config"
	"rss-knowledge-base/internal/handler"
	"rss-knowledge-base/internal/middleware"
	"rss-knowledge-base/internal/model"
	"rss-knowledge-base/internal/service"
	"rss-knowledge-base/internal/websocket"
)

func main() {
	cfg, err := config.Load("config.yaml")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	if err := os.MkdirAll("data", 0755); err != nil {
		log.Fatalf("Failed to create data directory: %v", err)
	}

	if err := model.InitDatabase(cfg.Database.Path); err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	crawlService := service.NewCrawlService(cfg)
	crawlService.Start()

	wsHub := websocket.NewHub()
	go wsHub.Run()

	r := gin.Default()

	r.Use(middleware.CORS())

	api := r.Group("/api")
	{
		feedHandler := handler.NewFeedHandler(crawlService)
		feedHandler.RegisterRoutes(api)

		articleHandler := handler.NewArticleHandler()
		articleHandler.RegisterRoutes(api)

		categoryHandler := handler.NewCategoryHandler()
		categoryHandler.RegisterRoutes(api)

		tagHandler := handler.NewTagHandler()
		tagHandler.RegisterRoutes(api)

		systemHandler := handler.NewSystemHandler()
		systemHandler.RegisterRoutes(api)

		aiHandler := handler.NewAIHandler(cfg)
		aiHandler.RegisterRoutes(api)
	}

	r.GET("/ws", func(c *gin.Context) {
		wsHub.HandleWebSocket(c)
	})

	go func() {
		if err := r.Run(cfg.Address()); err != nil {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	log.Printf("Server started on %s", cfg.Address())

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")
	crawlService.Stop()
}
