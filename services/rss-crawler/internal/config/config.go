package config

import (
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Server      ServerConfig      `yaml:"server"`
	Database    DatabaseConfig    `yaml:"database"`
	Meilisearch MeilisearchConfig `yaml:"meilisearch"`
	Ollama      OllamaConfig      `yaml:"ollama"`
	Crawler     CrawlerConfig     `yaml:"crawler"`
	AI          AIConfig          `yaml:"ai"`
}

type ServerConfig struct {
	Host string `yaml:"host"`
	Port int    `yaml:"port"`
}

type DatabaseConfig struct {
	Path string `yaml:"path"`
}

type MeilisearchConfig struct {
	Host      string `yaml:"host"`
	APIKey    string `yaml:"api_key"`
	IndexName string `yaml:"index_name"`
}

type OllamaConfig struct {
	Host    string `yaml:"host"`
	Model   string `yaml:"model"`
	Timeout int    `yaml:"timeout"`
}

type CrawlerConfig struct {
	Concurrent int    `yaml:"concurrent"`
	Timeout    int    `yaml:"timeout"`
	Retry      int    `yaml:"retry"`
	UserAgent  string `yaml:"user_agent"`
}

type AIConfig struct {
	Enabled   bool `yaml:"enabled"`
	BatchSize int  `yaml:"batch_size"`
}

func (c *Config) Address() string {
	return fmt.Sprintf("%s:%d", c.Server.Host, c.Server.Port)
}

func Load(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config: %w", err)
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	return &cfg, nil
}

func Save(path string, cfg *Config) error {
	data, err := yaml.Marshal(cfg)
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("failed to write config: %w", err)
	}

	return nil
}
