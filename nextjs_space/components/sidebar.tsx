
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Video, 
  FileText, 
  Share2, 
  Sparkles,
  Settings,
  User,
  LogOut
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  className?: string;
}

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard', emoji: '📊' },
  { icon: Video, label: 'Video', href: '/create/video', emoji: '🎬' },
  { icon: FileText, label: 'Blog', href: '/create/blog', emoji: '✍️' },
  { icon: Share2, label: 'Social Post', href: '/create/social', emoji: '📱' },
  { icon: Settings, label: 'WordPress', href: '/wordpress', emoji: '⚙️' },
];

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div className={cn("h-screen bg-[#0C1E43] text-white flex flex-col p-6 overflow-y-auto shadow-2xl", className)}>
      {/* Logo */}
      <div className="text-center mb-8 pb-5 border-b-2 border-[#00AEEF]">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Sparkles className="w-6 h-6 text-[#00AEEF]" />
          <h1 className="text-2xl font-bold text-[#00AEEF]">FacelessContent</h1>
        </div>
        <p className="text-xs text-[#FFA62B] font-semibold tracking-wide">
          Multi-Channel AI Platform
        </p>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-5 py-4 rounded-lg transition-all duration-300 border-l-3",
                "text-sm font-medium",
                isActive
                  ? "bg-gradient-to-r from-[#004E92] to-[#00AEEF] border-l-[#FFA62B] shadow-lg"
                  : "bg-white/5 border-l-transparent hover:bg-white/10 hover:border-l-[#FFA62B] hover:translate-x-1"
              )}
            >
              <span className="text-lg">{item.emoji}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div className="mt-auto pt-5 border-t border-white/10 space-y-2">
        <Link
          href="/account"
          className="flex items-center gap-3 px-5 py-4 rounded-lg transition-all duration-300 bg-white/5 hover:bg-white/10 text-sm font-medium"
        >
          <User className="w-5 h-5" />
          <span>Mijn Account</span>
        </Link>
        <button
          onClick={() => {
            // Add logout logic here
            console.log('Logout clicked');
          }}
          className="w-full flex items-center gap-3 px-5 py-4 rounded-lg transition-all duration-300 bg-white/5 hover:bg-red-500/20 text-sm font-medium text-red-300"
        >
          <LogOut className="w-5 h-5" />
          <span>Uitloggen</span>
        </button>
      </div>
    </div>
  );
}
