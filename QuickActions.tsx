import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { 
  Calendar, 
  Bell, 
  Settings, 
  MessageSquare,
  DollarSign,
  TrendingUp
} from "lucide-react";

const actions = [
  {
    icon: Calendar,
    label: "일정 관리",
    description: "가능한 시간 설정",
    color: "bg-blue-100 text-blue-600 hover:bg-blue-200",
  },
  {
    icon: MessageSquare,
    label: "메시지",
    description: "멘티 답변하기",
    badge: 5,
    color: "bg-purple-100 text-purple-600 hover:bg-purple-200",
  },
  {
    icon: Bell,
    label: "알림 설정",
    description: "세션 알림 관리",
    color: "bg-yellow-100 text-yellow-600 hover:bg-yellow-200",
  },
  {
    icon: DollarSign,
    label: "정산 확인",
    description: "수익 내역 보기",
    color: "bg-green-100 text-green-600 hover:bg-green-200",
  },
  {
    icon: TrendingUp,
    label: "목표 설정",
    description: "이번 달 목표",
    color: "bg-orange-100 text-orange-600 hover:bg-orange-200",
  },
  {
    icon: Settings,
    label: "설정",
    description: "프로필 및 환경설정",
    color: "bg-gray-100 text-gray-600 hover:bg-gray-200",
  },
];

export function QuickActions() {
  return (
    <Card className="p-6 border-0 shadow-lg">
      <div className="mb-6">
        <h3 className="mb-1">빠른 실행</h3>
        <p className="text-gray-600 text-sm">자주 사용하는 기능</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {actions.map((action, index) => (
          <button
            key={index}
            className="relative p-4 rounded-lg border hover:border-blue-300 hover:shadow-md transition-all text-left group"
          >
            {action.badge && (
              <div className="absolute top-2 right-2 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center text-xs">
                {action.badge}
              </div>
            )}
            <div className={`w-10 h-10 rounded-lg ${action.color} flex items-center justify-center mb-3 transition-transform group-hover:scale-110`}>
              <action.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm mb-0.5">{action.label}</p>
              <p className="text-xs text-gray-500">{action.description}</p>
            </div>
          </button>
        ))}
      </div>
    </Card>
  );
}
