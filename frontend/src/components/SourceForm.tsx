import { useState } from 'react'
import type { Source, SourceCreate, SourceType } from '@/lib/api'

interface SourceFormProps {
  initial?: Source
  onSubmit: (data: SourceCreate) => void
  onCancel: () => void
  loading?: boolean
}

const SOURCE_TYPES: { value: SourceType; label: string }[] = [
  { value: 'ckan_api',          label: 'CT Open Data (Socrata)' },
  { value: 'vision_gov',        label: 'Vision Assessor' },
  { value: 'land_records',      label: 'Land Records (Laredo/Granicus)' },
  { value: 'ct_sos',            label: 'CT Secretary of State' },
  { value: 'iqs_land_records',  label: 'IQS Land Records' },
  { value: 'patriot_assessor',  label: 'Patriot Properties Assessor' },
  { value: 'arcgis_parcels',    label: 'ArcGIS Parcels (GIS)' },
  { value: 'ct_courts',         label: 'CT Courts (Civil / Small Claims)' },
  { value: 'ct_tax',            label: 'CT Tax Collector' },
  { value: 'municipal_data',    label: 'Municipal Documents (Legistar)' },
]

const DEFAULT_URLS: Record<SourceType, string> = {
  // Verified live URLs as of 2026
  ckan_api:         'https://data.ct.gov',
  vision_gov:       'https://gis.vgsi.com/greenwichct/',
  land_records:     'https://www.uslandrecords.com/ctlr/',   // Avenu - covers 18 CT towns
  ct_sos:           'https://www.concord-sots.ct.gov',
  iqs_land_records: 'https://www.searchiqs.com/ctmilf/',     // SearchIQS - Milford CT
  patriot_assessor: 'https://manchester.patriotproperties.com/', // Manchester CT uses Patriot
  arcgis_parcels:   'https://cteco.uconn.edu/ctmaps/rest/services/Parcels/Parcels/FeatureServer/0',
  ct_courts:        'https://civilinquiry.jud.ct.gov/',
  ct_tax:           'https://www.mytaxbill.org',             // TaxSys (Grant Street Group)
  municipal_data:   'https://hartford.civicweb.net/Portal',  // Hartford uses CivicWeb
}

// These are real starter configs, not just placeholder hint text
const EXAMPLE_CONFIGS: Record<SourceType, string> = {
  ckan_api:         '{"dataset_id": "5mzw-sjtu", "dataset_name": "Real Estate Sales", "tags": ["property"]}',
  vision_gov:       '{"town": "Greenwich", "assessment_year": 2024, "use_playwright": false}',
  land_records:     '{"town": "Bloomfield", "days_back": 30}',
  ct_sos:           '{}',
  iqs_land_records: '{"town": "Milford", "days_back": 30}',
  patriot_assessor: '{"town": "Manchester", "assessment_year": 2024, "use_playwright": false}',
  arcgis_parcels:   '{"town": "Connecticut", "layer_id": 0, "field_map": {}}',
  ct_courts:        '{"case_type": "civil", "days_back": 30, "use_playwright": false}',
  ct_tax:           '{"town": "hartford", "platform": "taxsys", "levy_year": 2025, "status_filter": "all"}',
  municipal_data:   '{"town": "hartford", "platform": "civicweb", "days_back": 90, "document_types": ["agenda", "minutes"]}',
}

const initialType: SourceType = 'ckan_api'

export function SourceForm({ initial, onSubmit, onCancel, loading }: SourceFormProps) {
  const [form, setForm] = useState<SourceCreate>({
    name:          initial?.name          ?? '',
    source_type:   initial?.source_type   ?? initialType,
    base_url:      initial?.base_url      ?? DEFAULT_URLS[initialType],
    // Pre-fill with example for new sources; keep existing value when editing
    config_json:   initial?.config_json   ?? EXAMPLE_CONFIGS[initialType],
    cron_schedule: initial?.cron_schedule ?? '',
    is_active:     initial?.is_active     ?? true,
  })

  const handleTypeChange = (type: SourceType) => {
    setForm(f => ({
      ...f,
      source_type: type,
      base_url:    initial ? f.base_url    : DEFAULT_URLS[type],
      config_json: initial ? f.config_json : EXAMPLE_CONFIGS[type],
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      ...form,
      config_json:   form.config_json?.trim()   || null,
      cron_schedule: form.cron_schedule?.trim() || null,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
        <input
          required
          className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={form.name}
          onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Source Type</label>
        <select
          className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={form.source_type}
          onChange={e => handleTypeChange(e.target.value as SourceType)}
        >
          {SOURCE_TYPES.map(({ value, label }) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Base URL</label>
        <input
          required
          type="url"
          className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={form.base_url}
          onChange={e => setForm(f => ({ ...f, base_url: e.target.value }))}
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-1">
          <label className="block text-sm font-medium text-gray-700">
            Config JSON <span className="text-gray-400 font-normal">(optional)</span>
          </label>
          {/* Show "Use example" when the field is empty (common when editing old sources) */}
          {!form.config_json?.trim() && (
            <button
              type="button"
              onClick={() => setForm(f => ({ ...f, config_json: EXAMPLE_CONFIGS[f.source_type] }))}
              className="text-xs text-blue-600 hover:underline"
            >
              Use example
            </button>
          )}
        </div>
        <textarea
          rows={3}
          className="w-full border rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={form.config_json ?? ''}
          onChange={e => setForm(f => ({ ...f, config_json: e.target.value }))}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Cron Schedule <span className="text-gray-400 font-normal">(optional)</span>
        </label>
        <input
          className="w-full border rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={form.cron_schedule ?? ''}
          onChange={e => setForm(f => ({ ...f, cron_schedule: e.target.value }))}
          placeholder="0 2 * * *"
        />
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_active"
          checked={form.is_active}
          onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))}
          className="rounded border-gray-300"
        />
        <label htmlFor="is_active" className="text-sm font-medium text-gray-700">Active</label>
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Saving…' : initial ? 'Update Source' : 'Add Source'}
        </button>
      </div>
    </form>
  )
}
