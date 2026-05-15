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

type SystemConfig struct {
	Key       string    `gorm:"primaryKey;size:100" json:"key"`
	Value     string    `gorm:"type:text" json:"value"`
	UpdatedAt time.Time `json:"updated_at"`
}

func (SystemConfig) TableName() string {
	return "system_config"
}
