import React from 'react';
import { Box, Typography, Card, CardContent, Grid, Chip, LinearProgress } from '@mui/material';
import { BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = ['#6C63FF','#A78BFA','#00CEC9','#FF6B6B','#FDCB6E','#2ED573','#FF9FF3','#54A0FF','#5F27CD','#01A3A4'];
const tooltipStyle = { backgroundColor: 'rgba(20,20,40,0.95)', border: '1px solid rgba(108,99,255,0.2)', borderRadius: 12, fontSize: '0.8rem' };

export const DeptBarChart: React.FC<{ data: any[] }> = ({ data }) => {
  if (!data.length) return <Typography color="text.secondary" variant="body2">No data</Typography>;
  const chartData = data.slice(0, 8).map(d => ({ name: (d.department || 'N/A').slice(0, 12), experts: d.person_count, experience: Math.round(d.avg_experience || 0) }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#999' }} />
        <YAxis tick={{ fontSize: 11, fill: '#999' }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: '0.75rem' }} />
        <Bar dataKey="experts" fill="#6C63FF" radius={[4,4,0,0]} name="Experts" />
        <Bar dataKey="experience" fill="#A78BFA" radius={[4,4,0,0]} name="Avg Exp (yr)" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export const SkillPieChart: React.FC<{ data: any[] }> = ({ data }) => {
  if (!data.length) return <Typography color="text.secondary" variant="body2">No data</Typography>;
  const chartData = data.slice(0, 8).map(d => ({ name: d.name || d.category || 'N/A', value: d.demand ?? d.expert_count ?? d.skill_count ?? 1 }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie data={chartData} cx="50%" cy="50%" innerRadius={55} outerRadius={95} paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name.slice(0,10)} ${(percent*100).toFixed(0)}%`} labelLine={{ stroke: '#666' }}>
          {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Pie>
        <Tooltip contentStyle={tooltipStyle} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export const ProjectAreaChart: React.FC<{ data: any[] }> = ({ data }) => {
  if (!data.length) return <Typography color="text.secondary" variant="body2">No data</Typography>;
  const chartData = data.map(p => ({ name: p.status || 'Unknown', count: p.count || 0, budget: Math.round((p.avg_budget || 0) / 1000) }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
        <defs>
          <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#6C63FF" stopOpacity={0.4} /><stop offset="95%" stopColor="#6C63FF" stopOpacity={0} /></linearGradient>
          <linearGradient id="colorBudget" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#00CEC9" stopOpacity={0.4} /><stop offset="95%" stopColor="#00CEC9" stopOpacity={0} /></linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#999' }} />
        <YAxis tick={{ fontSize: 11, fill: '#999' }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: '0.75rem' }} />
        <Area type="monotone" dataKey="count" stroke="#6C63FF" fill="url(#colorCount)" name="Projects" />
        <Area type="monotone" dataKey="budget" stroke="#00CEC9" fill="url(#colorBudget)" name="Avg Budget (k$)" />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export const SkillRadarChart: React.FC<{ data: any[] }> = ({ data }) => {
  if (!data.length) return <Typography color="text.secondary" variant="body2">No data</Typography>;
  const chartData = data.slice(0, 6).map(d => ({ skill: (d.name || '').slice(0, 10), demand: d.demand ?? 50, experts: d.expert_count ?? 10 }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
        <PolarGrid stroke="rgba(255,255,255,0.1)" />
        <PolarAngleAxis dataKey="skill" tick={{ fontSize: 10, fill: '#999' }} />
        <PolarRadiusAxis tick={{ fontSize: 9, fill: '#666' }} />
        <Radar name="Demand" dataKey="demand" stroke="#FF6B6B" fill="#FF6B6B" fillOpacity={0.25} />
        <Radar name="Experts" dataKey="experts" stroke="#6C63FF" fill="#6C63FF" fillOpacity={0.25} />
        <Legend wrapperStyle={{ fontSize: '0.75rem' }} />
        <Tooltip contentStyle={tooltipStyle} />
      </RadarChart>
    </ResponsiveContainer>
  );
};

export const CollaborationChart: React.FC<{ data: any[] }> = ({ data }) => {
  if (!data.length) return <Typography color="text.secondary" variant="body2">No collaboration data</Typography>;
  const chartData = data.slice(0, 10).map(d => ({ name: `${(d.dept1||'').slice(0,6)}↔${(d.dept2||'').slice(0,6)}`, value: d.collaborations || 0 }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 10, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis type="number" tick={{ fontSize: 11, fill: '#999' }} />
        <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: '#999' }} width={90} />
        <Tooltip contentStyle={tooltipStyle} />
        <Bar dataKey="value" name="Collaborations" radius={[0,4,4,0]}>
          {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export const SkillDistChart: React.FC<{ data: any[] }> = ({ data }) => {
  if (!data.length) return <Typography color="text.secondary" variant="body2">No data</Typography>;
  const chartData = data.slice(0, 10).map(d => ({ name: (d.category || 'Other').slice(0, 14), skills: d.skill_count || 0, experts: d.expert_count || 0 }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#999' }} />
        <YAxis tick={{ fontSize: 11, fill: '#999' }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: '0.75rem' }} />
        <Bar dataKey="skills" fill="#FDCB6E" radius={[4,4,0,0]} name="Skills" />
        <Bar dataKey="experts" fill="#2ED573" radius={[4,4,0,0]} name="Experts" />
      </BarChart>
    </ResponsiveContainer>
  );
};
