import { Card } from "../ui/card";
import { Progress } from "../ui/progress";
import { Target, TrendingUp, Award } from "lucide-react";

const goals = [
  {
    icon: Target,
    title: "이번 달 세션 목표",
    current: 24,
    target: 30,
    unit: "회",
    color: "text-blue-600",
    progressColor: "bg-blue-600",
  },
  {
    icon: TrendingUp,
    title: "월 수익 목표",
    current: 1200000,
    target: 1500000,
    unit: "원",
    color: "text-green-600",
    progressColor: "bg-green-600",
  },
  {
    icon: Award,
    title: "평점 유지 목표",
    current: 4.9,
    target: 4.8,
    unit: "점",
    color: "text-yellow-600",
    progressColor: "bg-yellow-600",
    achieved: true,
  },
];

export function GoalProgress() {
  return (
    <Card className="p-6 border-0 shadow-lg">
      <div className="mb-6">
        <h3 className="mb-1">이번 달 목표</h3>
        <p className="text-gray-600 text-sm">진행 상황을 확인하세요</p>
      </div>

      <div className="space-y-6">
        {goals.map((goal, index) => {
          const progress = goal.achieved 
            ? 100 
            : Math.min((goal.current / goal.target) * 100, 100);
          
          return (
            <div key={index} className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center ${goal.color}`}>
                    <goal.icon className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-sm mb-0.5">{goal.title}</p>
                    <div className="flex items-baseline gap-2">
                      <span className={`${goal.color}`}>
                        {goal.unit === "원" 
                          ? `₩${goal.current.toLocaleString()}` 
                          : goal.current.toLocaleString()}
                      </span>
                      <span className="text-gray-400 text-sm">
                        / {goal.unit === "원" 
                          ? `₩${goal.target.toLocaleString()}` 
                          : goal.target.toLocaleString()} {goal.unit}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`${progress >= 100 ? 'text-green-600' : 'text-gray-600'}`}>
                    {progress.toFixed(0)}%
                  </span>
                </div>
              </div>
              <Progress 
                value={progress} 
                className="h-2"
              />
              {goal.achieved && (
                <p className="text-xs text-green-600">✓ 목표 달성!</p>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-6 border-t">
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
          <div>
            <p className="text-sm text-gray-600 mb-1">전체 달성률</p>
            <div className="text-2xl">85%</div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">목표까지</p>
            <p className="text-blue-600">6일 남음</p>
          </div>
        </div>
      </div>
    </Card>
  );
}
