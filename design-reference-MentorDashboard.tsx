import { MentorDashboardHeader } from "../components/mentor-dashboard/MentorDashboardHeader";
import { DashboardStats } from "../components/mentor-dashboard/DashboardStats";
import { GamificationCard } from "../components/mentor-dashboard/GamificationCard";
import { UpcomingSessions } from "../components/mentor-dashboard/UpcomingSessions";
import { RecentReviews } from "../components/mentor-dashboard/RecentReviews";
import { PerformanceChart } from "../components/mentor-dashboard/PerformanceChart";
import { QuickActions } from "../components/mentor-dashboard/QuickActions";
import { GoalProgress } from "../components/mentor-dashboard/GoalProgress";
import { MentorRanking } from "../components/mentor-dashboard/MentorRanking";
import { Footer } from "../components/Footer";

interface MentorDashboardProps {
  onLogoClick?: () => void;
}

export default function MentorDashboard({ onLogoClick }: MentorDashboardProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <MentorDashboardHeader onLogoClick={onLogoClick} />
      
      <main className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="mb-2">안녕하세요, 김태희님! 👋</h1>
          <p className="text-gray-600">
            오늘도 멋진 멘토링으로 누군가의 성장을 도와주세요
          </p>
        </div>

        {/* Stats Overview */}
        <div className="mb-8">
          <DashboardStats />
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-8 mb-8">
          {/* Left Column - 2 cols */}
          <div className="lg:col-span-2 space-y-8">
            <GamificationCard />
            <PerformanceChart />
            <UpcomingSessions />
          </div>

          {/* Right Column - 1 col */}
          <div className="space-y-8">
            <GoalProgress />
            <MentorRanking />
            <QuickActions />
          </div>
        </div>

        {/* Bottom Section */}
        <div className="grid lg:grid-cols-2 gap-8">
          <RecentReviews />
          
          {/* Additional Insights Card */}
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl p-8 text-white shadow-lg">
            <h3 className="text-white mb-4">💡 이번 주 인사이트</h3>
            <div className="space-y-4">
              <div className="p-4 bg-white/10 backdrop-blur-sm rounded-lg">
                <p className="text-sm text-white/90 mb-2">가장 인기있는 시간대</p>
                <p className="text-xl">평일 오후 2-4시</p>
              </div>
              <div className="p-4 bg-white/10 backdrop-blur-sm rounded-lg">
                <p className="text-sm text-white/90 mb-2">주요 상담 주제</p>
                <p className="text-xl">커리어 전환 (45%)</p>
              </div>
              <div className="p-4 bg-white/10 backdrop-blur-sm rounded-lg">
                <p className="text-sm text-white/90 mb-2">평균 응답 시간</p>
                <p className="text-xl">2.5시간</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
