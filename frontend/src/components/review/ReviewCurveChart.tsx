import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

interface ReviewCurveChartProps {
  data?: Array<{ day: number; predicted: number; actual?: number }>
  currentDay?: number
  loading?: boolean
}

const DEFAULT_DATA = [
  { day: 0, predicted: 1.0, actual: 1.0 },
  { day: 1, predicted: 0.58, actual: undefined },
  { day: 3, predicted: 0.42, actual: undefined },
  { day: 7, predicted: 0.28, actual: undefined },
  { day: 14, predicted: 0.18, actual: undefined },
  { day: 30, predicted: 0.1, actual: undefined },
  { day: 60, predicted: 0.05, actual: undefined },
]

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-background p-2.5 shadow-lg">
        <p className="text-xs font-medium">第 {label} 天</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-xs" style={{ color: entry.color }}>
            {entry.name}: {typeof entry.value === 'number' ? `${(entry.value * 100).toFixed(0)}%` : entry.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export function ReviewCurveChart({ data, currentDay = 1, loading }: ReviewCurveChartProps) {
  const chartData = data && data.length > 0 ? data : DEFAULT_DATA

  return (
    <div className="h-64 w-full">
      {loading ? (
        <div className="flex h-64 items-center justify-center text-muted-foreground">
          加载中...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 8, right: 16, left: -8, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="day"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: 'var(--border)' }}
              label={{
                value: '天数',
                position: 'insideBottomRight',
                offset: -8,
                fontSize: 11,
                className: 'fill-muted-foreground',
              }}
            />
            <YAxis
              domain={[0, 1]}
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: 'var(--border)' }}
              tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
              width={40}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              x={currentDay}
              stroke="#ef4444"
              strokeDasharray="4 4"
              label={{
                value: '今天',
                position: 'top',
                fontSize: 10,
                fill: '#ef4444',
              }}
            />
            <Line
              type="monotone"
              dataKey="predicted"
              name="预测"
              stroke="#6366f1"
              strokeWidth={2}
              dot={{ r: 3, fill: '#6366f1' }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="actual"
              name="实际"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 3, fill: '#10b981' }}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

export default ReviewCurveChart
