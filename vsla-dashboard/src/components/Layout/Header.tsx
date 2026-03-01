/* Header — top navigation bar */
import { NavLink } from 'react-router-dom';
import { COLORS } from '../../models/constants';

const navItems = [
  { to: '/', label: 'Overview' },
  { to: '/membership', label: 'Membership' },
  { to: '/savings', label: 'Savings & Social Fund' },
  { to: '/loans', label: 'Loans' },
  { to: '/compare', label: 'Compare Counties' },
];

const linkStyle: React.CSSProperties = {
  color: 'rgba(255,255,255,0.8)',
  textDecoration: 'none',
  padding: '8px 16px',
  borderRadius: 6,
  fontSize: 14,
  fontWeight: 500,
  transition: 'background 0.2s',
};

const activeLinkStyle: React.CSSProperties = {
  ...linkStyle,
  color: '#fff',
  background: 'rgba(255,255,255,0.15)',
};

export default function Header() {
  return (
    <header style={{
      background: `linear-gradient(135deg, ${COLORS.primary} 0%, ${COLORS.secondary} 100%)`,
      padding: '0 32px',
      display: 'flex',
      alignItems: 'center',
      gap: 24,
      height: 56,
      boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        fontSize: 18, fontWeight: 700, color: '#fff',
        letterSpacing: 0.5, marginRight: 24,
      }}>
        📊 VSLA Dashboard
      </div>
      <nav style={{ display: 'flex', gap: 4 }}>
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            style={({ isActive }) => isActive ? activeLinkStyle : linkStyle}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
