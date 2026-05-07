package model

import "time"

type Article struct {
	ID          int64      `gorm:"primaryKey;autoIncrement" json:"id"`
	FeedID      int64      `gorm:"index;not null" json:"feed_id"`
	Title       string     `gorm:"size:512;not null" json:"title"`
	Link        string     `gorm:"size:2048;not null" json:"link"`
	Content     string     `gorm:"type:text" json:"content"`
	ContentHash string     `gorm:"size:64;uniqueIndex" json:"content_hash"`
	Summary     string     `gorm:"type:text" json:"summary"`
	Author      string     `gorm:"size:255" json:"author"`
	PublishedAt *time.Time `gorm:"index" json:"published_at"`
	CrawledAt   *time.Time `json:"crawled_at"`
	ReadStatus  int        `gorm:"default:0;index" json:"read_status"`
	CreatedAt   time.Time  `json:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at"`

	Feed *Feed  `gorm:"foreignKey:FeedID" json:"feed,omitempty"`
	Tags []Tag  `gorm:"many2many:article_tags" json:"tags,omitempty"`
}

func (Article) TableName() string {
	return "articles"
}
