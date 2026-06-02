import { useState, useCallback, type KeyboardEvent } from 'react'
import { Search, Filter, X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface SearchFilters {
  category?: string
  difficulty?: string
}

interface KnowledgeSearchProps {
  onSearch: (query: string, filters: SearchFilters) => void
  categories?: string[]
  loading?: boolean
}

const DIFFICULTIES = [
  { value: 'L1', label: '入门' },
  { value: 'L2', label: '基础' },
  { value: 'L3', label: '进阶' },
  { value: 'L4', label: '竞赛' },
]

export function KnowledgeSearch({ onSearch, categories = [], loading }: KnowledgeSearchProps) {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<string>('')
  const [difficulty, setDifficulty] = useState<string>('')

  const handleSearch = useCallback(() => {
    onSearch(query, { category: category || undefined, difficulty: difficulty || undefined })
  }, [query, category, difficulty, onSearch])

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const handleClear = () => {
    setQuery('')
    setCategory('')
    setDifficulty('')
    onSearch('', {})
  }

  const hasFilters = category || difficulty || query

  return (
    <div className="flex flex-col gap-3 rounded-xl border bg-card p-4 shadow-sm">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="搜索知识点..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="pl-9"
          />
        </div>
        <Button onClick={handleSearch} disabled={loading}>
          <Search className="mr-1 h-4 w-4" />
          搜索
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />

        {/* Category filter */}
        <select
          className="h-9 rounded-md border border-input bg-background px-3 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">全部分类</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        {/* Difficulty filter */}
        <div className="flex gap-1">
          {DIFFICULTIES.map((d) => (
            <button
              key={d.value}
              onClick={() => setDifficulty(difficulty === d.value ? '' : d.value)}
              className={cn(
                'rounded-md border px-2.5 py-1 text-xs font-medium transition-colors',
                difficulty === d.value
                  ? 'border-primary bg-primary text-primary-foreground'
                  : 'border-input bg-background text-muted-foreground hover:bg-accent'
              )}
            >
              {d.label}
            </button>
          ))}
        </div>

        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={handleClear}>
            <X className="mr-1 h-3.5 w-3.5" />
            清除筛选
          </Button>
        )}
      </div>
    </div>
  )
}

export default KnowledgeSearch
