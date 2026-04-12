import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import type { IntermediateOutcome, ImmediateOutcome, Output, Activity } from '../types';

export default function FrameworkPage() {
  const navigate = useNavigate();

  const [intOutcomes, setIntOutcomes] = useState<IntermediateOutcome[]>([]);
  const [immOutcomes, setImmOutcomes] = useState<ImmediateOutcome[]>([]);
  const [outputs, setOutputs] = useState<Output[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);

  const [selIO, setSelIO] = useState('');
  const [selIMO, setSelIMO] = useState('');
  const [selOut, setSelOut] = useState('');

  // Load intermediate outcomes on mount
  useEffect(() => {
    api.get('/intermediate-outcomes').then((r) => setIntOutcomes(r.data.data));
  }, []);

  // Cascade: load immediate outcomes
  useEffect(() => {
    setImmOutcomes([]);
    setOutputs([]);
    setActivities([]);
    setSelIMO('');
    setSelOut('');
    if (!selIO) return;
    api.get(`/intermediate-outcomes/${selIO}/immediate-outcomes`).then((r) => setImmOutcomes(r.data.data));
  }, [selIO]);

  // Cascade: load outputs
  useEffect(() => {
    setOutputs([]);
    setActivities([]);
    setSelOut('');
    if (!selIMO) return;
    api.get(`/immediate-outcomes/${selIMO}/outputs`).then((r) => setOutputs(r.data.data));
  }, [selIMO]);

  // Cascade: load activities
  useEffect(() => {
    setActivities([]);
    if (!selOut) return;
    api.get(`/outputs/${selOut}/activities`).then((r) => setActivities(r.data.data));
  }, [selOut]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Implementation Plan</h1>

      {/* Cascading dropdowns */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <label className="block">
          <span className="text-sm font-medium text-gray-700">Intermediate Outcome</span>
          <select
            value={selIO}
            onChange={(e) => setSelIO(e.target.value)}
            className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="">-- Select --</option>
            {intOutcomes.map((io) => (
              <option key={io.id} value={io.id}>
                {io.code}: {io.description.substring(0, 60)}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Immediate Outcome</span>
          <select
            value={selIMO}
            onChange={(e) => setSelIMO(e.target.value)}
            disabled={!selIO}
            className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 disabled:opacity-50"
          >
            <option value="">-- Select --</option>
            {immOutcomes.map((imo) => (
              <option key={imo.id} value={imo.id}>
                {imo.code}: {imo.description.substring(0, 60)}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Output</span>
          <select
            value={selOut}
            onChange={(e) => setSelOut(e.target.value)}
            disabled={!selIMO}
            className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 disabled:opacity-50"
          >
            <option value="">-- Select --</option>
            {outputs.map((o) => (
              <option key={o.id} value={o.id}>
                {o.code}: {o.description.substring(0, 60)}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Activity</span>
          <select
            disabled={!selOut}
            onChange={(e) => {
              if (e.target.value) navigate(`/activity/${e.target.value}`);
            }}
            className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 disabled:opacity-50"
          >
            <option value="">-- Select --</option>
            {activities.map((a) => (
              <option key={a.id} value={a.id}>
                {a.code}: {a.description.substring(0, 60)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* Activity cards */}
      {activities.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Activities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activities.map((act) => (
              <div
                key={act.id}
                onClick={() => navigate(`/activity/${act.id}`)}
                className="cursor-pointer rounded-lg border bg-white p-4 shadow-sm hover:shadow-md transition"
              >
                <p className="font-mono text-xs text-primary-600 mb-1">{act.code}</p>
                <p className="text-sm text-gray-800 line-clamp-3">{act.description}</p>
                <div className="mt-2 flex items-center justify-between">
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      act.status === 'Completed'
                        ? 'bg-green-100 text-green-800'
                        : act.status === 'On track'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {act.status}
                  </span>
                  {act.budget_holder && (
                    <span className="text-xs text-gray-500">{act.budget_holder.name}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full framework tree when no selection */}
      {!selIO && intOutcomes.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Results Framework Overview</h2>
          <div className="space-y-2">
            {intOutcomes.map((io) => (
              <div key={io.id} className="rounded-lg border bg-white p-4 shadow-sm">
                <button
                  onClick={() => setSelIO(io.id)}
                  className="text-left w-full"
                >
                  <span className="font-mono text-sm text-primary-600">{io.code}</span>
                  <span className="ml-2 text-sm text-gray-700">{io.description}</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
