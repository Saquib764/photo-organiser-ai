<script setup lang="ts">
const {
  persons,
  loading,
  error,
  peopleAvailable,
  personThumbnailUrl,
  fetchPersons,
  updatePerson,
  deletePerson,
  isDeleting,
} = usePersons()

const { requestStatus } = useWorkspaceStatusDisplay()

const documentActiveTab = useState('document-active-tab', () => 'library')

onMounted(() => {
  void fetchPersons()
})

watch(peopleAvailable, (available) => {
  if (available) {
    void fetchPersons()
  }
})

async function saveName(personId: string, name: string) {
  const trimmed = name.trim()
  if (!trimmed) {
    return
  }
  await updatePerson(personId, { name: trimmed })
}

async function saveDescription(personId: string, description: string) {
  await updatePerson(personId, { description: description.trim() })
}

async function onDeletePerson(personId: string) {
  const deleted = await deletePerson(personId)
  if (deleted) {
    await requestStatus()
  }
}
</script>

<template>
  <div class="mx-auto max-w-5xl space-y-6">
    <div>
      <h2 class="text-lg font-semibold text-white">
        People
      </h2>
      <p class="mt-1 text-sm text-gray-500">
        Rename people and add roles (e.g. Bride, Groom). Run people detection in Library state first.
      </p>
    </div>

    <div
      v-if="!peopleAvailable"
      class="tf-card !p-6 text-sm text-gray-400"
    >
      No people detected yet.
      <button
        type="button"
        class="ml-1 text-primary-400 underline decoration-primary-400/40 underline-offset-2 hover:text-primary-300"
        @click="documentActiveTab = 'library'"
      >
        Open Library state
      </button>
      and start the People step after thumbnails are ready.
    </div>

    <div
      v-else-if="loading"
      class="text-sm text-gray-500"
    >
      Loading people…
    </div>

    <div
      v-else-if="error"
      class="text-sm text-red-400"
    >
      {{ error }}
    </div>

    <div
      v-else-if="persons.length === 0"
      class="tf-card !p-6 text-sm text-gray-400"
    >
      No faces were grouped into people. Try rerunning people detection with clearer close-up photos.
    </div>

    <ul
      v-else
      class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <li
        v-for="person in persons"
        :key="person.id"
        class="tf-card flex flex-col gap-3 !p-4"
      >
        <div class="flex items-start gap-3">
          <img
            :src="personThumbnailUrl(person)"
            :alt="person.name"
            class="size-16 shrink-0 rounded-lg object-cover ring-1 ring-gray-800"
          >
          <div class="min-w-0 flex-1 space-y-2">
            <div class="flex items-start gap-2">
              <UInput
                :model-value="person.name"
                size="sm"
                class="min-w-0 flex-1"
                @change="saveName(person.id, ($event.target as HTMLInputElement).value)"
              />
              <UButton
                size="xs"
                color="error"
                variant="ghost"
                icon="i-heroicons-trash"
                :loading="isDeleting(person.id)"
                :disabled="isDeleting(person.id)"
                aria-label="Delete person"
                @click="onDeletePerson(person.id)"
              />
            </div>
            <p class="text-xs text-gray-500">
              {{ person.image_count }} {{ person.image_count === 1 ? 'photo' : 'photos' }}
              · {{ person.face_count }} {{ person.face_count === 1 ? 'face' : 'faces' }}
            </p>
          </div>
        </div>
        <UTextarea
          :model-value="person.description"
          placeholder="Description (e.g. Bride, Groom's mother)"
          :rows="2"
          size="sm"
          class="w-full"
          @change="saveDescription(person.id, ($event.target as HTMLTextAreaElement).value)"
        />
      </li>
    </ul>
  </div>
</template>
