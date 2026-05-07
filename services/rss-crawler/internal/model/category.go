package model

import "time"

type Category struct {
	ID        int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	Name      string    `gorm:"size:255;not null" json:"name"`
	Icon      string    `gorm:"size:100" json:"icon"`
	SortOrder int       `gorm:"default:0" json:"sort_order"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`

	Feeds []Feed `gorm:"foreignKey:CategoryID" json:"feeds,omitempty"`
}

func (Category) TableName() string {
	return "categories"
}
