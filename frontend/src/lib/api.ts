import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// ── Types ─────────────────────────────────────────────────────────────────────

export type SourceType = 'ckan_api' | 'vision_gov' | 'land_records' | 'ct_sos'
export type JobStatus = 'pending' | 'running' | 'success' | 'failed' | 'cancelled'
export type LandRecordType = 'deed' | 'mortgage' | 'lien' | 'release' | 'other'

export interface Source {
  id: number
  name: string
  source_type: SourceType
  base_url: string
  config_json: string | null
  cron_schedule: string | null
  is_active: boolean
  last_scraped_at: string | null
  created_at: string
  updated_at: string
}

export interface SourceCreate {
  name: string
  source_type: SourceType
  base_url: string
  config_json?: string | null
  cron_schedule?: string | null
  is_active?: boolean
}

export interface ScrapeJob {
  id: number
  source_id: number
  status: JobStatus
  triggered_by: string
  started_at: string | null
  finished_at: string | null
  records_found: number
  records_new: number
  records_updated: number
  records_skipped: number
  error_message: string | null
  log_text?: string | null
  created_at: string
  updated_at: string
}

export interface PropertyRecord {
  id: number
  source_id: number
  scrape_job_id: number | null
  fingerprint: string
  town: string | null
  parcel_id: string | null
  map_lot: string | null
  street_number: string | null
  street_name: string | null
  unit: string | null
  zip_code: string | null
  owner_name: string | null
  owner_address: string | null
  assessed_value: number | null
  land_value: number | null
  building_value: number | null
  assessment_year: number | null
  property_class: string | null
  acreage: number | null
  building_sqft: number | null
  year_built: number | null
  quality_score: number | null
  created_at: string
  updated_at: string
}

export interface PropertyStats {
  total: number
  towns: string[]
  avg_assessed_value: number | null
  min_assessed_value: number | null
  max_assessed_value: number | null
  years: number[]
}

export interface LandRecord {
  id: number
  source_id: number
  scrape_job_id: number | null
  fingerprint: string
  town: string | null
  record_type: LandRecordType | null
  grantor: string | null
  grantee: string | null
  recorded_date: string | null
  book: string | null
  page: string | null
  instrument_no: string | null
  consideration: number | null
  parcel_id: string | null
  description: string | null
  document_url: string | null
  quality_score: number | null
  created_at: string
  updated_at: string
}

export interface LandRecordStats {
  total: number
  towns: string[]
  record_types: Record<string, number>
}

export interface BusinessRecord {
  id: number
  source_id: number
  scrape_job_id: number | null
  fingerprint: string
  business_id: string | null
  business_name: string | null
  business_type: string | null
  status: string | null
  formation_date: string | null
  dissolution_date: string | null
  principal_office: string | null
  registered_agent: string | null
  agent_address: string | null
  annual_report_year: number | null
  naics_code: string | null
  state_of_formation: string | null
  quality_score: number | null
  created_at: string
  updated_at: string
}

export interface BusinessStats {
  total: number
  by_type: Record<string, number>
  by_status: Record<string, number>
}

export interface OpenDataRecord {
  id: number
  source_id: number
  scrape_job_id: number | null
  fingerprint: string
  dataset_id: string
  dataset_name: string | null
  row_id: string
  data_json: Record<string, unknown> | null
  tags: string[] | null
  quality_score: number | null
  created_at: string
  updated_at: string
}

export interface DatasetInfo {
  dataset_id: string
  dataset_name: string | null
  record_count: number
}

export interface DashboardSummary {
  record_counts: {
    properties: number
    land_records: number
    businesses: number
    open_data: number
  }
  running_jobs: number
  last_job_at: string | null
  last_job_status: JobStatus | null
}

export interface JobHistoryDay {
  date: string
  success: number
  failed: number
  running: number
  pending: number
  cancelled: number
}

// ── API Functions ─────────────────────────────────────────────────────────────

// Sources
export const getSources = () => client.get<Source[]>('/sources').then(r => r.data)
export const getSource = (id: number) => client.get<Source>(`/sources/${id}`).then(r => r.data)
export const createSource = (data: SourceCreate) => client.post<Source>('/sources', data).then(r => r.data)
export const updateSource = (id: number, data: Partial<SourceCreate>) => client.put<Source>(`/sources/${id}`, data).then(r => r.data)
export const deleteSource = (id: number) => client.delete(`/sources/${id}`)
export const triggerSource = (id: number) => client.post<{ job_id: number; message: string }>(`/sources/${id}/trigger`).then(r => r.data)
export const toggleSource = (id: number) => client.patch<Source>(`/sources/${id}/toggle`).then(r => r.data)

// Jobs
export const getJobs = (params?: { source_id?: number; status?: JobStatus; limit?: number; offset?: number }) =>
  client.get<ScrapeJob[]>('/jobs', { params }).then(r => r.data)
export const getJob = (id: number) => client.get<ScrapeJob>(`/jobs/${id}`).then(r => r.data)
export const cancelJob = (id: number) => client.post<ScrapeJob>(`/jobs/${id}/cancel`).then(r => r.data)
export const deleteJob = (id: number) => client.delete(`/jobs/${id}`)

// Properties
export const getProperties = (params?: Record<string, unknown>) =>
  client.get<PropertyRecord[]>('/properties', { params }).then(r => r.data)
export const getProperty = (id: number) => client.get<PropertyRecord>(`/properties/${id}`).then(r => r.data)
export const getPropertyStats = () => client.get<PropertyStats>('/properties/stats').then(r => r.data)

// Land Records
export const getLandRecords = (params?: Record<string, unknown>) =>
  client.get<LandRecord[]>('/land-records', { params }).then(r => r.data)
export const getLandRecord = (id: number) => client.get<LandRecord>(`/land-records/${id}`).then(r => r.data)
export const getLandRecordStats = () => client.get<LandRecordStats>('/land-records/stats').then(r => r.data)

// Businesses
export const getBusinesses = (params?: Record<string, unknown>) =>
  client.get<BusinessRecord[]>('/businesses', { params }).then(r => r.data)
export const getBusiness = (id: number) => client.get<BusinessRecord>(`/businesses/${id}`).then(r => r.data)
export const getBusinessStats = () => client.get<BusinessStats>('/businesses/stats').then(r => r.data)

// Open Data
export const getOpenData = (params?: Record<string, unknown>) =>
  client.get<OpenDataRecord[]>('/open-data', { params }).then(r => r.data)
export const getOpenDataRecord = (id: number) => client.get<OpenDataRecord>(`/open-data/${id}`).then(r => r.data)
export const getDatasets = () => client.get<DatasetInfo[]>('/open-data/datasets').then(r => r.data)

// Dashboard
export const getDashboardSummary = () => client.get<DashboardSummary>('/dashboard/summary').then(r => r.data)
export const getJobHistory = (days = 30) => client.get<JobHistoryDay[]>('/dashboard/job-history', { params: { days } }).then(r => r.data)

// Exports (returns direct URL)
export const getExportUrl = (type: string, format: 'csv' | 'xlsx') =>
  `/api/v1/exports/${type}.${format}`
