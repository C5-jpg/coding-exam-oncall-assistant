export type NavKey = 'product' | 'useCases' | 'pricing' | 'blog' | 'resources';

export const navItems = [
  { key: 'product', label: 'Product', href: '#product', dropdown: false },
  { key: 'useCases', label: 'Use Cases', href: '#use-cases', dropdown: true },
  { key: 'pricing', label: 'Pricing', href: '#pricing', dropdown: false },
  { key: 'blog', label: 'Blog', href: '#blog', dropdown: false },
  { key: 'resources', label: 'Resources', href: '#resources', dropdown: true },
] as const;

export const useCaseMenu = [
  { icon: '◎', label: 'Professional', href: '#use-cases' },
  { icon: '</>', label: 'Frontend', href: '#use-cases' },
  { icon: '▱', label: 'Fullstack', href: '#use-cases' },
];

export const resourcesMenu = [
  { label: 'Documentation', href: '#resources' },
  { label: 'Changelog', href: '#resources' },
  { label: 'Support', href: '#resources' },
  { label: 'Press', href: '#resources' },
  { label: 'Releases', href: '#resources' },
];
