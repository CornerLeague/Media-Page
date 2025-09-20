import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface FeedListProps {
  sortBy?: 'relevance' | 'trending' | 'recent'
  contentType?: 'breaking' | 'all'
}

interface Article {
  id: string
  title: string
  summary: string
  source: string
  publishedAt: string
  readTime: number
}

export function FeedList({ sortBy = 'relevance', contentType = 'all' }: FeedListProps) {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Mock data for now - in a real app this would fetch from API
    const mockArticles: Article[] = [
      {
        id: '1',
        title: 'NFL Week 3 Highlights: Upsets and Standout Performances',
        summary: 'Major upsets shake up playoff predictions as underdogs deliver stunning victories...',
        source: 'ESPN',
        publishedAt: '2025-09-18T14:30:00Z',
        readTime: 3
      },
      {
        id: '2',
        title: 'Trade Deadline Approaching: Which Teams Are Buyers vs Sellers?',
        summary: 'Analysis of team positions and potential moves as the trade deadline looms...',
        source: 'The Athletic',
        publishedAt: '2025-09-18T12:15:00Z',
        readTime: 5
      },
      {
        id: '3',
        title: 'Rising Stars: Rookie Performance Review Mid-Season',
        summary: 'Evaluating the impact of this year\'s rookie class at the halfway point...',
        source: 'Bleacher Report',
        publishedAt: '2025-09-18T10:45:00Z',
        readTime: 4
      }
    ]

    // Simulate loading
    setTimeout(() => {
      setArticles(mockArticles)
      setLoading(false)
    }, 1000)
  }, [sortBy, contentType])

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {articles.map((article) => (
        <Card key={article.id} className="hover:shadow-md transition-shadow cursor-pointer">
          <CardHeader>
            <CardTitle className="text-lg">{article.title}</CardTitle>
            <CardDescription className="flex items-center gap-2">
              <span>{article.source}</span>
              <span>•</span>
              <span>{article.readTime} min read</span>
              <span>•</span>
              <span>{new Date(article.publishedAt).toLocaleDateString()}</span>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">{article.summary}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}