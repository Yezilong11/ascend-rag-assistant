package model

import "time"

type Feed struct {
	ID            int64      `gorm:"primaryKey;autoIncrement" json:"id"`
	Name          string     `gorm:"size:255;not null" json:"name"`
	URL           string     `gorm:"size:2048;not null" json:"url"`
	Description   string     `gorm:"type:text" json:"description"`
	CategoryID    int64      `gorm:"index" json:"category_id"`
	CrawlInterval int        `gorm:"default:60" json:"crawl_interval"`
	LastCrawl     *time.Time `json:"last_crawl"`
	NextCrawl     *time.Time `json:"next_crawl"`
	Status        string     `gorm:"size:50;default:'active'" json:"status"`
	ErrorMessage  string     `gorm:"type:text" json:"error_message"`
	CreatedAt     time.Time  `json:"created_at"`
	UpdatedAt     time.Time  `json:"updated_at"`

	Category *Category `gorm:"foreignKey:CategoryID" json:"category,omitempty"`
}

func (Feed) TableName() string {
	return "feeds"
}
