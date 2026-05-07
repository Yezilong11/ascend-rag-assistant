package crawler

import (
	"context"
	"time"

	"github.com/mmcdole/gofeed"
)

type Crawler struct {
	parser    *gofeed.Parser
	userAgent string
	timeout   time.Duration
}

func NewCrawler(userAgent string, timeout time.Duration) *Crawler {
	return &Crawler{
		parser:    gofeed.NewParser(),
		userAgent: userAgent,
		timeout:   timeout,
	}
}

func (c *Crawler) Fetch(url string) ([]*gofeed.Item, error) {
	ctx, cancel := context.WithTimeout(context.Background(), c.timeout)
	defer cancel()

	c.parser.UserAgent = c.userAgent
	feed, err := c.parser.ParseURLWithContext(url, ctx)
	if err != nil {
		return nil, err
	}

	return feed.Items, nil
}
