import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

// Sample data (from your Year 3 MERL Workplan)
const initialData = [
  {
    objective: "1. Quality Delivery of MERL Functions",
    activity: "Maintain and implement COSME M&E framework, Theory of Change alignment, and MIS",
    deliverable: "Updated MERL framework & MIS",
    indicator: "≥90% MERL deliverables on time",
    timeline: "Q1",
    responsible: "MERL Officer",
    progress: ""
  },
  {
    objective: "2. Managing Project Results & Partner Accountability",
    activity: "Conduct performance/results review sessions",
    deliverable: "Review meeting minutes & action points",
    indicator: "≥1 review session quarterly",
    timeline: "Quarterly",
    responsible: "MERL Officer",
    progress: ""
  },
  {
    objective: "3. Learning, Knowledge Management & Influencing",
    activity: "Produce and disseminate learning products (case studies, stories, lessons)",
    deliverable: "≥3 learning products",
    indicator: "≥3 learning products disseminated",
    timeline: "Bi-annual/Annual",
    responsible: "MERL Officer + Comms",
    progress: ""
  },
  {
    objective: "4. Capacity Strengthening of Staff, WROs, YLOs",
    activity: "Conduct MERL training & coaching sessions",
    deliverable: "Training reports",
    indicator: "≥2 capacity sessions conducted",
    timeline: "Semi-annual",
    responsible: "MERL Officer",
    progress: ""
  },
  {
    objective: "5. Safeguarding & GEI Integration in MERL",
    activity: "Conduct quarterly GEI & safeguarding compliance checks",
    deliverable: "Compliance reports",
    indicator: "4 reports annually",
    timeline: "Quarterly",
    responsible: "MERL Officer",
    progress: ""
  }
];

export default function MERLTracker() {
  const [data, setData] = useState(initialData);

  const handleProgressChange = (index, value) => {
    const updated = [...data];
    updated[index].progress = value;
    setData(updated);
  };

  return (
    <div className="p-6 grid gap-6">
      <h1 className="text-2xl font-bold">MERL Year 3 Workplan Tracker</h1>
      {data.map((row, index) => (
        <Card key={index} className="shadow-md">
          <CardContent className="p-4 grid gap-2">
            <h2 className="text-lg font-semibold">{row.objective}</h2>
            <p><strong>Activity:</strong> {row.activity}</p>
            <p><strong>Deliverable:</strong> {row.deliverable}</p>
            <p><strong>Indicator:</strong> {row.indicator}</p>
            <p><strong>Timeline:</strong> {row.timeline}</p>
            <p><strong>Responsible:</strong> {row.responsible}</p>
            <div>
              <label className="block text-sm font-medium mb-1">Progress Update</label>
              <Textarea
                placeholder="Enter progress..."
                value={row.progress}
                onChange={(e) => handleProgressChange(index, e.target.value)}
              />
            </div>
            <Button className="mt-2 w-fit">Save Update</Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
