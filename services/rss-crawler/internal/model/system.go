package model

import "time"

type Tag struct {
	ID        int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	Name      string    `gorm:"size:255;not null;uniqueIndex" json:"name"`
	Color     string    `gorm:"size:20" json:"color"`
	CreatedAt time.Time `json:"created_at"`

	Articles []Article `gorm:"many2many:article_tags" json:"articles,omitempty"`
}

func (Tag) TableName() string {
	return "tags"
}

type AIAnalysisCache struct {
	ID          int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	ContentHash string    `gorm:"size:64;uniqueIndex" json:"content_hash"`
	Summary     string    `gorm:"type:text" json:"summary"`
	Keywords    string    `gorm:"type:text" json:"keywords"`
	Sentiment   string    `gorm:"size:50" json:"sentiment"`
	Theme       string    `gorm:"size:100" json:"theme"`
	CreatedAt   time.Time `json:"created_at"`
}

func (AIAnalysisCache) TableName() string {
	return "ai_analysis_cache"
}

type SystemConfig struct {
	Key       string    `gorm:"primaryKey;size:100" json:"key"`
	Value     string    `gorm:"type:text" json:"value"`
	UpdatedAt time.Time `json:"updated_at"`
}

func (SystemConfig) TableName() string {
	return "system_config"
}
