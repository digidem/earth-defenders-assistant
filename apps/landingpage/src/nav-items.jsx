import {
  Home,
  Info,
  Wrench,
  Star,
  TrendingUp,
  BookOpen,
  Mail,
} from "lucide-react";
import Index from "./pages/Index.jsx";

/**
 * Central place for defining the navigation items. Used for navigation components and routing.
 */
export const navItems = [
  {
    title: "Home",
    to: "/",
    icon: <Home className="h-4 w-4" />,
    page: <Index />,
  },
  {
    title: "About",
    to: "/about",
    icon: <Info className="h-4 w-4" />,
    page: <div>About Page</div>,
  },
  {
    title: "Tools",
    to: "/tools",
    icon: <Wrench className="h-4 w-4" />,
    page: <div>Tools Page</div>,
  },
  {
    title: "Reviews",
    to: "/reviews",
    icon: <Star className="h-4 w-4" />,
    page: <div>Reviews Page</div>,
  },
  {
    title: "Trends",
    to: "/trends",
    icon: <TrendingUp className="h-4 w-4" />,
    page: <div>Trends Page</div>,
  },
  {
    title: "Blog",
    to: "/blog",
    icon: <BookOpen className="h-4 w-4" />,
    page: <div>Blog Page</div>,
  },
  {
    title: "Contact",
    to: "/contact",
    icon: <Mail className="h-4 w-4" />,
    page: <div>Contact Page</div>,
  },
];
