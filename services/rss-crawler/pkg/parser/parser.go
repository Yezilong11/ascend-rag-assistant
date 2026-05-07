package parser

import (
	"regexp"
	"strings"
	"time"

	"github.com/mmcdole/gofeed"
)

type Parser struct{}

func NewParser() *Parser {
	return &Parser{}
}

func (p *Parser) CleanContent(content string) string {
	content = regexp.MustCompile(`<script[^>]*>.*?</script>`).ReplaceAllString(content, "")
	content = regexp.MustCompile(`<style[^>]*>.*?</style>`).ReplaceAllString(content, "")
	content = regexp.MustCompile(`<[^>]+>`).ReplaceAllString(content, "")
	content = regexp.MustCompile(`\s+`).ReplaceAllString(content, " ")
	content = strings.TrimSpace(content)
	return content
}

func (p *Parser) Parse(item *gofeed.Item) map[string]string {
	content := item.Content
	if content == "" {
		content = item.Description
	}

	return map[string]string{
		"title":    item.Title,
		"link":     item.Link,
		"content":  p.CleanContent(content),
		"author":   p.getAuthor(item),
		"published": p.getPublished(item),
	}
}

func (p *Parser) getAuthor(item *gofeed.Item) string {
	if item.Author != nil {
		return item.Author.Name
	}
	return ""
}

func (p *Parser) getPublished(item *gofeed.Item) string {
	if item.Published != nil {
		return item.Published.Format(time.RFC3339)
	}
	return ""
}
