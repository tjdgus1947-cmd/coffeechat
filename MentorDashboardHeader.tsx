import { Bell, User, Menu, X } from "lucide-react";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { useState } from "react";
import { LogoImage } from "../LogoImage";

interface MentorDashboardHeaderProps {
  onLogoClick?: () => void;
}

export function MentorDashboardHeader({ onLogoClick }: MentorDashboardHeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <button 
            onClick={onLogoClick}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <LogoImage variant="light" className="h-10" />
            <Badge className="bg-purple-100 text-purple-700 hover:bg-purple-200">
              멘토
            </Badge>
          </button>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <a href="#" className="text-gray-900 transition">
              대시보드
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition">
              일정관리
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition">
              멘티관리
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition">
              수익현황
            </a>
          </nav>

          <div className="hidden md:flex items-center gap-4">
            <button className="relative p-2 hover:bg-gray-100 rounded-lg">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            <Button variant="ghost" className="gap-2">
              <User className="w-5 h-5" />
              마이페이지
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 flex flex-col gap-4">
            <a href="#" className="text-gray-900 transition">
              대시보드
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition">
              일정관리
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition">
              멘티관리
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition">
              수익현황
            </a>
            <div className="flex flex-col gap-2 pt-2">
              <Button variant="ghost" className="w-full gap-2">
                <Bell className="w-5 h-5" />
                알림
              </Button>
              <Button variant="ghost" className="w-full gap-2">
                <User className="w-5 h-5" />
                마이페이지
              </Button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
