import type {
  PersonDeleteResponse,
  PersonListResponse,
  PersonSummary,
  PersonUpdateRequest,
} from '~/types/persons'

export function usePersons() {
  const { apiBase } = useImageUrls()
  const { peopleAvailable } = useWorkspaceStatusDisplay()

  const persons = useState<PersonSummary[]>('workspace-persons', () => [])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const deletingPersonIds = ref<Set<string>>(new Set())

  function personThumbnailUrl(person: PersonSummary): string {
    if (person.thumbnail_url.startsWith('http')) {
      return person.thumbnail_url
    }
    return `${apiBase}${person.thumbnail_url}`
  }

  async function fetchPersons() {
    loading.value = true
    error.value = null
    try {
      const data = await $fetch<PersonListResponse>(`${apiBase}/api/v1/persons`)
      persons.value = data.persons
    }
    catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load people'
      persons.value = []
    }
    finally {
      loading.value = false
    }
  }

  async function updatePerson(personId: string, body: PersonUpdateRequest) {
    const updated = await $fetch<PersonSummary>(
      `${apiBase}/api/v1/persons/${encodeURIComponent(personId)}`,
      { method: 'PATCH', body },
    )
    const index = persons.value.findIndex(person => person.id === personId)
    if (index !== -1) {
      persons.value[index] = updated
    }
    return updated
  }

  function isDeleting(personId: string): boolean {
    return deletingPersonIds.value.has(personId)
  }

  async function deletePerson(personId: string): Promise<boolean> {
    const person = persons.value.find(entry => entry.id === personId)
    const label = person?.name ?? personId
    const confirmed = confirm(
      `Delete "${label}"?\n\nThis removes them from the people list and clears their tags from all photos.`,
    )
    if (!confirmed) {
      return false
    }

    const nextDeleting = new Set(deletingPersonIds.value)
    nextDeleting.add(personId)
    deletingPersonIds.value = nextDeleting
    error.value = null

    try {
      await $fetch<PersonDeleteResponse>(
        `${apiBase}/api/v1/persons/${encodeURIComponent(personId)}`,
        { method: 'DELETE' },
      )
      persons.value = persons.value.filter(entry => entry.id !== personId)
      return true
    }
    catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete person'
      return false
    }
    finally {
      const done = new Set(deletingPersonIds.value)
      done.delete(personId)
      deletingPersonIds.value = done
    }
  }

  return {
    persons,
    loading,
    error,
    peopleAvailable,
    personThumbnailUrl,
    fetchPersons,
    updatePerson,
    deletePerson,
    isDeleting,
  }
}
