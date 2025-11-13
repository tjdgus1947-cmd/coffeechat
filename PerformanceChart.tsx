import { Card } from "../ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const sessionData = [
  { month: "6월", sessions: 12, revenue: 600000 },
  { month: "7월", sessions: 18, revenue: 900000 },
  { month: "8월", sessions: 15, revenue: 750000 },
  { month: "9월", sessions: 22, revenue: 1100000 },
  { month: "10월", sessions: 24, revenue: 1200000 },
  { month: "11월", sessions: 28, revenue: 1400000 },
];

const ratingData = [
  { month: "6월", rating: 4.5 },
  { month: "7월", rating: 4.6 },
  { month: "8월", rating: 4.7 },
  { month: "9월", rating: 4.8 },
  { month: "10월", rating: 4.9 },
  { month: "11월", rating: 4.9 },
];

export function PerformanceChart() {
  return (
    <Card className="p-6 border-0 shadow-lg">
      <h3 className="mb-6">성과 분석</h3>
      
      <Tabs defaultValue="sessions" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-6">
          <TabsTrigger value="sessions">멘토링 횟수</TabsTrigger>
          <TabsTrigger value="revenue">수익</TabsTrigger>
          <TabsTrigger value="rating">평점 추이</TabsTrigger>
        </TabsList>

        <TabsContent value="sessions">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sessionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="month" 
                stroke="#888888"
                fontSize={12}
              />
              <YAxis 
                stroke="#888888"
                fontSize={12}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
              />
              <Bar 
                dataKey="sessions" 
                fill="#3b82f6" 
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              지난 6개월 동안 <span className="text-blue-600">총 119회</span>의 멘토링 진행
            </p>
          </div>
        </TabsContent>

        <TabsContent value="revenue">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={sessionData}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="month" 
                stroke="#888888"
                fontSize={12}
              />
              <YAxis 
                stroke="#888888"
                fontSize={12}
                tickFormatter={(value) => `₩${(value / 1000)}K`}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
                formatter={(value: number) => [`₩${value.toLocaleString()}`, '수익']}
              />
              <Area 
                type="monotone" 
                dataKey="revenue" 
                stroke="#10b981" 
                fillOpacity={1} 
                fill="url(#colorRevenue)" 
              />
            </AreaChart>
          </ResponsiveContainer>
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              지난 6개월 총 수익: <span className="text-green-600">₩5,950,000</span>
            </p>
          </div>
        </TabsContent>

        <TabsContent value="rating">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={ratingData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="month" 
                stroke="#888888"
                fontSize={12}
              />
              <YAxis 
                stroke="#888888"
                fontSize={12}
                domain={[4, 5]}
                ticks={[4.0, 4.2, 4.4, 4.6, 4.8, 5.0]}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
              />
              <Line 
                type="monotone" 
                dataKey="rating" 
                stroke="#eab308" 
                strokeWidth={3}
                dot={{ fill: '#eab308', r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              평점이 지속적으로 향상되고 있습니다! 현재 평점: <span className="text-yellow-600">4.9/5.0</span>
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </Card>
  );
}
