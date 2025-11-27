import { Card } from "../ui/card";
import { 
  Calendar, 
  Star, 
  TrendingUp, 
  Wallet, 
  Users,
  Clock
} from "lucide-react";

const stats = [
  {
    icon: Calendar,
    label: "이번 달 세션",
    value: "24",
    change: "+12%",
    trend: "up",
    color: "bg-blue-100 text-blue-600",
  },
  {
    icon: Star,
    label: "평균 평점",
    value: "4.9",
    change: "+0.2",
    trend: "up",
    color: "bg-yellow-100 text-yellow-600",
  },
  {
    icon: Wallet,
    label: "이번 달 수익",
    value: "₩1,200,000",
    change: "+18%",
    trend: "up",
    color: "bg-green-100 text-green-600",
  },
  {
    icon: Users,
    label: "총 멘티",
    value: "127",
    change: "+8",
    trend: "up",
    color: "bg-purple-100 text-purple-600",
  },
];

export function DashboardStats() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <Card key={index} className="p-6 border-0 shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-start justify-between mb-4">
            <div className={`w-12 h-12 rounded-xl ${stat.color} flex items-center justify-center`}>
              <stat.icon className="w-6 h-6" />
            </div>
            <div className={`text-sm flex items-center gap-1 ${
              stat.trend === "up" ? "text-green-600" : "text-red-600"
            }`}>
              <TrendingUp className="w-4 h-4" />
              {stat.change}
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-gray-600 text-sm">{stat.label}</p>
            <div>{stat.value}</div>
          </div>
        </Card>
      ))}
    </div>
  );
}
