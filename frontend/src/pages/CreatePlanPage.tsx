import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card, Form, Input, Select, DatePicker, InputNumber, Button, Table, Space,
  Typography, message, Divider, Row, Col, Switch, Tooltip, Tag, Flex,
} from 'antd';
import { PlusOutlined, DeleteOutlined, SaveOutlined } from '@ant-design/icons';
import api from '../api';
import { useAuthStore } from '../store';
import dayjs from 'dayjs';

const MONTHS = Array.from({ length: 12 }, (_, i) => ({
  value: i + 1,
  label: dayjs().month(i).format('MMMM'),
}));

const HUBS = [
  'MEESA Regional Hub',
  'West & Central Africa Regional Hub',
  'Southern Africa Regional Hub',
  'Asia Regional Hub',
  'Americas Regional Hub',
  'Global Hub',
];

const COUNTRIES = ['Kenya', 'Uganda', 'Tanzania', 'Ethiopia', 'Somalia', 'South Sudan'];
const FISCAL_YEARS = ['FY25', 'FY26', 'FY27', 'FY28'];

/** COSME fiscal‑year quarter: Q1 = Jul‑Sep, Q2 = Oct‑Dec, Q3 = Jan‑Mar, Q4 = Apr‑Jun */
function deriveQuarter(month: number): string {
  if (month >= 7 && month <= 9) return 'Q1';
  if (month >= 10 && month <= 12) return 'Q2';
  if (month >= 1 && month <= 3) return 'Q3';
  return 'Q4';
}

export default function CreatePlanPage() {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [lookups, setLookups] = useState<any>({});
  const [lineItems, setLineItems] = useState<any[]>([
    { key: 1, item_type: 'Stock', quantity: 1, estimated_unit_price: 0, estimated_warehousing_cost: 0, estimated_transport_cost: 0, currency_code: 'KES', is_stock_on_hand_available: false, quantity_available: 0, fiscal_year: 'FY26' },
  ]);
  const user = useAuthStore((s) => s.user);

  // ── Load lookup data ─────────────────────────────────────────────
  useEffect(() => {
    Promise.all([
      api.get('/admin/projects'),
      api.get('/admin/locations'),
      api.get('/admin/material-groups'),
      api.get('/admin/units-of-measure'),
      api.get('/admin/funding-sources'),
      api.get('/admin/managers'),
      api.get('/admin/sourcing-methods'),
    ]).then(([projects, locations, mgs, uoms, fs, managers, sm]) => {
      const locs = locations.data as any[];
      setLookups({
        projects: projects.data,
        locations: locs,
        materialGroups: mgs.data,
        uoms: uoms.data,
        fundingSources: fs.data,
        managers: managers.data,
        sourcingMethods: sm.data,
      });

      // Default location to "Kilifi Office" for all initial line items
      const kilifi = locs.find((l: any) => l.locationName === 'Kilifi Office');
      if (kilifi) {
        setLineItems((prev) =>
          prev.map((li) => (li.location_id ? li : { ...li, location_id: kilifi.id }))
        );
      }
    });
  }, []);

  // ── Fetch next tracking number when plan type + FY are set ──────
  const fetchNextTrackingNo = useCallback(async (planType?: string, fy?: string) => {
    const type = planType || form.getFieldValue('type_of_procurement_plan');
    const financialYear = fy || form.getFieldValue('financial_year');
    if (!type || !financialYear) return;
    try {
      const { data } = await api.get('/admin/next-tracking-no', { params: { type, fy: financialYear } });
      form.setFieldsValue({ tracking_no: data.tracking_no });
    } catch {
      // leave manual entry as fallback
    }
  }, [form]);

  // ── Auto‑populate header fields from PII Office Data (project) ──
  const onProjectChange = (projectId: string) => {
    const project = lookups.projects?.find((p: any) => p.id === projectId);
    if (!project) return;

    const fields: Record<string, any> = {
      project_code_cost_centre: project.projectCode,
    };

    // VLOOKUP equivalents from PII Office Data
    if (project.globalRegionalHub) fields.global_regional_hub = project.globalRegionalHub;
    if (project.countryOffice) fields.country_office = project.countryOffice;
    if (project.fadSpadNumber) fields.fad_spad_number = project.fadSpadNumber;
    if (project.fundingSourceId) fields.funding_source_id = project.fundingSourceId;
    if (project.donorName) fields.donor_name = project.donorName;
    if (project.startDate) fields.start_date = dayjs(project.startDate);
    if (project.endDate) fields.end_date = dayjs(project.endDate);

    form.setFieldsValue(fields);

    // Re-generate tracking number with the current planType + FY
    fetchNextTrackingNo();
  };

  // ── Handle plan type change → re-generate tracking no ──────────
  const onPlanTypeChange = (type: string) => {
    fetchNextTrackingNo(type, undefined);
  };

  // ── Handle FY change → re-generate tracking no + push FY to line items
  const onFYChange = (fy: string) => {
    fetchNextTrackingNo(undefined, fy);
    // Auto-populate fiscal year on every line item
    setLineItems((prev) => prev.map((li) => ({ ...li, fiscal_year: fy })));
  };

  // ── Line‑item helpers ──────────────────────────────────────────
  const addLineItem = () => {
    const nextKey = Math.max(...lineItems.map((li) => li.key), 0) + 1;
    const fy = form.getFieldValue('financial_year') || '';
    const kilifi = lookups.locations?.find((l: any) => l.locationName === 'Kilifi Office');
    setLineItems([
      ...lineItems,
      {
        key: nextKey, item_type: 'Stock', quantity: 1,
        estimated_unit_price: 0, estimated_warehousing_cost: 0, estimated_transport_cost: 0,
        currency_code: 'KES', is_stock_on_hand_available: false, quantity_available: 0,
        fiscal_year: fy,
        location_id: kilifi?.id || undefined,
      },
    ]);
  };

  const removeLineItem = (key: number) => {
    if (lineItems.length <= 1) { message.warning('At least one line item is required'); return; }
    setLineItems(lineItems.filter((li) => li.key !== key));
  };

  const updateLineItem = (key: number, field: string, value: any) => {
    setLineItems((prev) => prev.map((li) => {
      if (li.key !== key) return li;
      const updated = { ...li, [field]: value };

      // ── Auto-derive quarter from month (COSME FY) ──
      if (field === 'month' && typeof value === 'number') {
        updated.quarter = deriveQuarter(value);
      }

      // ── Auto-populate sourcing method from material group ──
      if (field === 'material_group_id') {
        const mg = lookups.materialGroups?.find((m: any) => m.id === value);
        if (mg?.defaultSourcingMethodId) {
          updated.sourcing_method_id = mg.defaultSourcingMethodId;
        }
      }

      return updated;
    }));
  };

  const calcTotal = (li: any) => {
    const qty = li.quantity || 0;
    const price = li.estimated_unit_price || 0;
    return qty * price + (li.estimated_warehousing_cost || 0) + (li.estimated_transport_cost || 0);
  };

  // ── Submit ─────────────────────────────────────────────────────
  const onFinish = async (values: any) => {
    if (lineItems.length === 0) { message.error('Add at least one line item'); return; }

    const missingDesc = lineItems.some((li) => !li.item_description?.trim());
    if (missingDesc) { message.error('All line items must have a description'); return; }

    const missingFields = lineItems.some((li) => !li.location_id || !li.material_group_id || !li.uom_id || li.month == null || !li.fiscal_year);
    if (missingFields) {
      const missing = lineItems.map((li, i) => {
        const gaps: string[] = [];
        if (!li.location_id) gaps.push('location');
        if (!li.material_group_id) gaps.push('material group');
        if (!li.uom_id) gaps.push('UoM');
        if (li.month == null) gaps.push('month');
        if (!li.fiscal_year) gaps.push('fiscal year');
        return gaps.length ? `Item #${i + 1}: ${gaps.join(', ')}` : null;
      }).filter(Boolean);
      message.error(`Missing fields — ${missing.join('; ')}`);
      return;
    }

    setLoading(true);
    try {
      const trackingNo = values.tracking_no;
      const payload = {
        tracking_no: trackingNo,
        global_regional_hub: values.global_regional_hub || undefined,
        country_office: values.country_office || undefined,
        project_id: values.project_id,
        type_of_procurement_plan: values.type_of_procurement_plan,
        department_manager_id: values.department_manager_id,
        fad_spad_number: values.fad_spad_number || undefined,
        project_code_cost_centre: values.project_code_cost_centre,
        funding_source_id: values.funding_source_id,
        donor_name: values.donor_name || undefined,
        financial_year: values.financial_year || undefined,
        currency: values.currency || 'KES',
        start_date: values.start_date.format('YYYY-MM-DD'),
        end_date: values.end_date.format('YYYY-MM-DD'),
        line_items: lineItems.map((li, i) => ({
          line_item_ref: `${trackingNo}-${String(i + 1).padStart(3, '0')}`,
          location_id: li.location_id,
          activity_number: li.activity_number || undefined,
          material_group_id: li.material_group_id,
          item_description: li.item_description,
          uom_id: li.uom_id,
          quantity: li.quantity,
          currency_code: li.currency_code,
          estimated_unit_price: li.estimated_unit_price,
          estimated_warehousing_cost: li.estimated_warehousing_cost || 0,
          estimated_transport_cost: li.estimated_transport_cost || 0,
          month: li.month,
          quarter: deriveQuarter(li.month),
          fiscal_year: li.fiscal_year,
          item_type: li.item_type || undefined,
          is_stock_on_hand_available: li.is_stock_on_hand_available || false,
          quantity_available: li.quantity_available || 0,
        })),
      };

      const { data } = await api.post('/procurement-plans', payload);
      message.success(`Plan ${data.tracking_no} created with ${data.line_items?.length || 0} line items`);
      navigate(`/plans/${data.id}`);
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || err.response?.data?.error || 'Failed to create plan';
      message.error(typeof errorMsg === 'string' ? errorMsg : 'Failed to create plan');
    } finally {
      setLoading(false);
    }
  };

  // ── Helper to get sourcing method name for a line item ─────────
  const getSourcingMethodName = (li: any): string => {
    if (!li.sourcing_method_id) return '';
    const sm = lookups.sourcingMethods?.find((s: any) => s.id === li.sourcing_method_id);
    return sm?.methodName || '';
  };

  return (
    <div>
      <Typography.Title level={4}>Create Procurement Plan</Typography.Title>

      <Form form={form} layout="vertical" onFinish={onFinish}
        initialValues={{ global_regional_hub: 'MEESA Regional Hub', country_office: 'Kenya', financial_year: 'FY26', currency: 'KES' }}>

        {/* Template Header Section */}
        <Card title="Plan Header — Template Info" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col xs={24} sm={12} lg={4}>
              <Form.Item name="tracking_no" label="Tracking No" rules={[{ required: true }]}
                tooltip="Auto-generated from Plan Type + Financial Year">
                <Input placeholder="Auto-generated" readOnly style={{ background: '#f5f5f5' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={4}>
              <Form.Item name="type_of_procurement_plan" label="Plan Type" rules={[{ required: true }]}>
                <Select options={[
                  { value: 'Project', label: 'Project' },
                  { value: 'Department', label: 'Department' },
                ]} placeholder="Select type" onChange={onPlanTypeChange} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={3}>
              <Form.Item name="financial_year" label="Financial Year">
                <Select options={FISCAL_YEARS.map((fy) => ({ value: fy, label: fy }))} onChange={onFYChange} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={5}>
              <Form.Item name="global_regional_hub" label="Global/Regional Hub"
                tooltip="Auto-populated from project, editable">
                <Select placeholder="Select hub"
                  popupMatchSelectWidth={false}
                  options={HUBS.map((h) => ({ value: h, label: h }))}
                  optionRender={(option) => (
                    <div style={{ padding: '2px 0' }}>
                      <div style={{ fontWeight: 600 }}>{option.label}</div>
                    </div>
                  )}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={4}>
              <Form.Item name="country_office" label="Country Office"
                tooltip="Auto-populated from project, editable">
                <Select options={COUNTRIES.map((c) => ({ value: c, label: c }))} placeholder="Select country" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={4}>
              <Form.Item name="currency" label="Currency">
                <Select options={[{ value: 'KES', label: 'KES' }, { value: 'EUR', label: 'EUR' }]} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col xs={24} sm={12} lg={6}>
              <Form.Item name="project_id" label="Project / Department" rules={[{ required: true }]}>
                <Select
                  showSearch
                  optionFilterProp="label"
                  onChange={onProjectChange}
                  placeholder="Select to auto-fill fields below"
                  popupMatchSelectWidth={false}
                  options={lookups.projects?.map((p: any) => ({
                    value: p.id,
                    label: `${p.projectCode} — ${p.projectName}`,
                  }))}
                  optionRender={(option) => {
                    const p = lookups.projects?.find((pr: any) => pr.id === option.value);
                    return (
                      <div style={{ padding: '4px 0' }}>
                        <div style={{ fontWeight: 600 }}>{p?.projectCode} — {p?.projectName}</div>
                        <div style={{ fontSize: 11, color: '#888' }}>
                          {p?.description || 'No description'}{p?.globalRegionalHub ? ` · ${p.globalRegionalHub}` : ''}
                        </div>
                      </div>
                    );
                  }}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Form.Item name="department_manager_id" label="Project / Department Manager" rules={[{ required: true }]}>
                <Select
                  showSearch
                  optionFilterProp="label"
                  placeholder="Select manager"
                  popupMatchSelectWidth={false}
                  options={lookups.managers?.map((u: any) => ({
                    value: u.id,
                    label: `${u.fullName} (${u.email})`,
                  }))}
                  optionRender={(option) => {
                    const u = lookups.managers?.find((m: any) => m.id === option.value);
                    return (
                      <div style={{ padding: '4px 0' }}>
                        <div style={{ fontWeight: 600 }}>{u?.fullName}</div>
                        <div style={{ fontSize: 11, color: '#888' }}>{u?.email}</div>
                      </div>
                    );
                  }}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={4}>
              <Form.Item name="fad_spad_number" label="FAD/SPAD Number"
                tooltip="Auto-populated from project">
                <Input placeholder="e.g. 100374" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={4}>
              <Form.Item name="project_code_cost_centre" label="Project Code / Cost Centre" rules={[{ required: true }]}>
                <Input placeholder="e.g. FECNO" readOnly style={{ background: '#f5f5f5' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={4}>
              <Form.Item name="funding_source_id" label="Funding Source" rules={[{ required: true }]}
                tooltip="Auto-populated from project">
                <Select
                  showSearch
                  optionFilterProp="label"
                  allowClear
                  popupMatchSelectWidth={false}
                  options={lookups.fundingSources?.map((f: any) => ({
                    value: f.id,
                    label: f.sourceName,
                  }))}
                  optionRender={(option) => {
                    const f = lookups.fundingSources?.find((fs: any) => fs.id === option.value);
                    return (
                      <div style={{ padding: '4px 0' }}>
                        <div style={{ fontWeight: 600 }}>{f?.sourceName}</div>
                        <div style={{ fontSize: 11, color: '#888' }}>{f?.description || 'Funding source'}</div>
                      </div>
                    );
                  }}
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col xs={24} sm={12} lg={6}>
              <Form.Item name="donor_name" label="Donor Name"
                tooltip="Auto-populated from project">
                <Input placeholder="e.g. GAC" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={4}>
              <Form.Item name="start_date" label="Start Date" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} lg={4}>
              <Form.Item name="end_date" label="End Date" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        <Card
          title="Line Items"
          extra={<Button icon={<PlusOutlined />} onClick={addLineItem}>Add Item</Button>}
          style={{ marginBottom: 16 }}
        >
          {lineItems.map((li, idx) => (
            <div key={li.key} style={{ padding: 12, marginBottom: 8, background: idx % 2 === 0 ? '#fafafa' : '#fff', borderRadius: 6 }}>
              <Row gutter={8} align="middle">
                <Col span={1}><strong>#{idx + 1}</strong></Col>
                <Col span={3}>
                  <Select value={li.material_group_id} onChange={(v) => updateLineItem(li.key, 'material_group_id', v)}
                    placeholder="Material Group" style={{ width: '100%' }} allowClear showSearch optionFilterProp="label"
                    popupMatchSelectWidth={false}
                    options={lookups.materialGroups?.map((m: any) => ({ value: m.id, label: `${m.groupNumber} — ${m.groupName}` }))}
                    optionRender={(option) => {
                      const m = lookups.materialGroups?.find((mg: any) => mg.id === option.value);
                      const sm = m?.defaultSourcingMethod?.methodName;
                      return (
                        <div style={{ padding: '4px 0' }}>
                          <div style={{ fontWeight: 600 }}>{m?.groupNumber}</div>
                          <div style={{ fontSize: 11, color: '#555' }}>{m?.groupName}</div>
                          {sm && <div style={{ fontSize: 10, color: '#1890ff' }}>Sourcing: {sm}</div>}
                        </div>
                      );
                    }}
                  />
                </Col>
                <Col span={2}>
                  <Select value={li.item_type} onChange={(v) => updateLineItem(li.key, 'item_type', v)} style={{ width: '100%' }}
                    options={[{ value: 'Stock', label: 'Stock' }, { value: 'Asset', label: 'Asset' }, { value: 'Service', label: 'Service' }]} />
                </Col>
                <Col span={4}>
                  <Input value={li.item_description} onChange={(e) => updateLineItem(li.key, 'item_description', e.target.value)}
                    placeholder="Description *" />
                </Col>
                <Col span={2}>
                  <InputNumber value={li.quantity} onChange={(v) => updateLineItem(li.key, 'quantity', v)} min={0.01} style={{ width: '100%' }}
                    placeholder="Qty" />
                </Col>
                <Col span={2}>
                  <Select value={li.uom_id} onChange={(v) => updateLineItem(li.key, 'uom_id', v)}
                    placeholder="UoM" style={{ width: '100%' }} allowClear showSearch optionFilterProp="label"
                    popupMatchSelectWidth={false}
                    options={lookups.uoms?.map((u: any) => ({ value: u.id, label: `${u.uomCode} — ${u.uomName}` }))}
                    optionRender={(option) => {
                      const u = lookups.uoms?.find((um: any) => um.id === option.value);
                      return (
                        <div style={{ padding: '2px 0' }}>
                          <span style={{ fontWeight: 600 }}>{u?.uomCode}</span>
                          <span style={{ fontSize: 11, color: '#888', marginLeft: 6 }}>{u?.uomName}</span>
                        </div>
                      );
                    }}
                  />
                </Col>
                <Col span={3}>
                  <InputNumber value={li.estimated_unit_price} onChange={(v) => updateLineItem(li.key, 'estimated_unit_price', v)}
                    min={0} style={{ width: '100%' }} placeholder="Unit Price"
                    formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={(value) => Number(value?.replace(/,/g, '') || 0)} />
                </Col>
                <Col span={2}>
                  <Select value={li.currency_code} onChange={(v) => updateLineItem(li.key, 'currency_code', v)} style={{ width: '100%' }}
                    options={[{ value: 'KES' }, { value: 'EUR' }]} />
                </Col>
                <Col span={3}>
                  <Select value={li.location_id} onChange={(v) => updateLineItem(li.key, 'location_id', v)}
                    placeholder="Location *" style={{ width: '100%' }}
                    popupMatchSelectWidth={false}
                    options={lookups.locations?.map((l: any) => ({
                      value: l.id,
                      label: l.locationName,
                    }))}
                    optionRender={(option) => {
                      const l = lookups.locations?.find((loc: any) => loc.id === option.value);
                      return (
                        <div style={{ padding: '2px 0' }}>
                          <div style={{ fontWeight: 600 }}>{l?.locationName}</div>
                          {l?.address && <div style={{ fontSize: 11, color: '#888' }}>{l.address}</div>}
                        </div>
                      );
                    }}
                  />
                </Col>
                <Col span={1}>
                  <Button icon={<DeleteOutlined />} danger size="small" onClick={() => removeLineItem(li.key)} />
                </Col>
              </Row>
              <Row gutter={8} style={{ marginTop: 4 }}>
                <Col span={1} />
                <Col span={3}>
                  <Select value={li.month} onChange={(v) => updateLineItem(li.key, 'month', v)}
                    placeholder="Month *" style={{ width: '100%' }}
                    popupMatchSelectWidth={false}
                    options={MONTHS}
                    optionRender={(option) => {
                      const m = option.value as number;
                      const q = deriveQuarter(m);
                      return (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '2px 0' }}>
                          <span style={{ fontWeight: 500 }}>{option.label}</span>
                          <Tag color="blue" style={{ margin: 0, fontSize: 10 }}>{q}</Tag>
                        </div>
                      );
                    }}
                  />
                </Col>
                <Col span={2}>
                  {li.month ? (
                    <Tag color="blue" style={{ lineHeight: '30px' }}>{deriveQuarter(li.month)}</Tag>
                  ) : (
                    <Tag style={{ lineHeight: '30px' }}>Quarter</Tag>
                  )}
                </Col>
                <Col span={2}>
                  <Input value={li.fiscal_year} readOnly style={{ background: '#f5f5f5' }}
                    placeholder="FY (auto)" />
                </Col>
                <Col span={3}>
                  <InputNumber value={li.estimated_warehousing_cost} onChange={(v) => updateLineItem(li.key, 'estimated_warehousing_cost', v)}
                    min={0} style={{ width: '100%' }} placeholder="Warehouse Cost"
                    formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={(value) => Number(value?.replace(/,/g, '') || 0)} />
                </Col>
                <Col span={3}>
                  <InputNumber value={li.estimated_transport_cost} onChange={(v) => updateLineItem(li.key, 'estimated_transport_cost', v)}
                    min={0} style={{ width: '100%' }} placeholder="Transport Cost"
                    formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={(value) => Number(value?.replace(/,/g, '') || 0)} />
                </Col>
                <Col span={2}>
                  <Input value={li.activity_number} onChange={(e) => updateLineItem(li.key, 'activity_number', e.target.value)}
                    placeholder="Activity #" />
                </Col>
                {getSourcingMethodName(li) && (
                  <Col span={3}>
                    <Tag color="green" style={{ lineHeight: '30px', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {getSourcingMethodName(li)}
                    </Tag>
                  </Col>
                )}
                <Col span={2}>
                  <Switch checked={li.is_stock_on_hand_available} onChange={(v) => updateLineItem(li.key, 'is_stock_on_hand_available', v)}
                    checkedChildren="Stock" unCheckedChildren="No Stock" />
                </Col>
                {li.is_stock_on_hand_available && (
                  <Col span={2}>
                    <InputNumber value={li.quantity_available} onChange={(v) => updateLineItem(li.key, 'quantity_available', v)}
                      min={0} style={{ width: '100%' }} placeholder="Avail" />
                  </Col>
                )}
                <Col flex="auto" style={{ textAlign: 'right', fontWeight: 600 }}>
                  Total: {calcTotal(li).toLocaleString()} {li.currency_code}
                </Col>
              </Row>
            </div>
          ))}

          <Divider />
          <Row justify="end">
            <Typography.Text strong style={{ fontSize: 16 }}>
              Grand Total (KES): {lineItems.filter((l) => l.currency_code === 'KES').reduce((s, l) => s + calcTotal(l), 0).toLocaleString()} KES
              {' | '}
              Grand Total (EUR): {lineItems.filter((l) => l.currency_code === 'EUR').reduce((s, l) => s + calcTotal(l), 0).toLocaleString()} EUR
            </Typography.Text>
          </Row>
        </Card>

        <Space>
          <Button onClick={() => navigate('/plans')}>Cancel</Button>
          <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading} size="large">
            Create Plan
          </Button>
        </Space>
      </Form>
    </div>
  );
}
