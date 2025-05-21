<script lang="ts">
  import { getContext } from 'svelte';
  import { toast } from 'svelte-sonner';
  import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

  const i18n = getContext('i18n');

  let activeTab: 'documents' | 'chat' = 'documents';

  let file: File | null = null;
  let fileContent = '';
  let observations = '';

  let messages: { role: string; content: string }[] = [];
  let question = '';

  let showSaveDialog = false;
  let saveContext = '';
  let lastQA: { question: string; answer: string } | null = null;

  const handleFileChange = (e: Event) => {
    const target = e.target as HTMLInputElement;
    const f = target.files ? target.files[0] : null;
    file = f;
    fileContent = '';
    if (!f) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      fileContent = ev.target?.result as string;
    };
    reader.readAsText(f);
  };

  const toBase64 = (f: File) =>
    new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve((reader.result as string).split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(f);
    });

  const submitDocument = async () => {
    if (!file || !observations.trim()) {
      toast.error($i18n.t('Observations'));
      return;
    }
    const documento_base64 = await toBase64(file);
    const payload = {
      documento_base64,
      observacoes: observations,
      usuario_admin: 'admin_id',
      status: 'aprovado',
      timestamp: new Date().toISOString()
    };
    await fetch('/api/training/document', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(() => {});
    toast.success($i18n.t('Document sent'));
    file = null;
    fileContent = '';
    observations = '';
  };

  const sendMessage = async () => {
    if (!question.trim()) return;
    messages = [...messages, { role: 'user', content: question }];
    const res = await fetch('/api/training/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    })
      .then((r) => r.json())
      .catch(() => ({ answer: '' }));
    messages = [...messages, { role: 'assistant', content: res.answer }];
    lastQA = { question, answer: res.answer };
    question = '';
  };

  const openSaveDialog = () => {
    if (!lastQA) return;
    saveContext = '';
    showSaveDialog = true;
  };

  const saveToVector = async () => {
    if (!saveContext.trim() || !lastQA) {
      toast.error($i18n.t('Context is required before saving'));
      return;
    }
    const payload = {
      pergunta_admin: lastQA.question,
      resposta_llm: lastQA.answer,
      observacoes: saveContext,
      usuario_admin: 'admin_id',
      status: 'salvar_no_vetor',
      timestamp: new Date().toISOString()
    };
    await fetch('/api/training/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(() => {});
    showSaveDialog = false;
    toast.success($i18n.t('Document sent'));
  };
</script>

<div class="flex flex-col h-full">
  <div class="flex border-b mb-4 space-x-2">
    <button
      class="px-4 py-2 rounded-t-lg focus:outline-none {activeTab==='documents' ? 'bg-gray-200 dark:bg-gray-800' : ''}"
      on:click={() => (activeTab = 'documents')}
    >{$i18n.t('Upload Document')}</button>
    <button
      class="px-4 py-2 rounded-t-lg focus:outline-none {activeTab==='chat' ? 'bg-gray-200 dark:bg-gray-800' : ''}"
      on:click={() => (activeTab = 'chat')}
    >{$i18n.t('Chat History')}</button>
  </div>

  {#if activeTab === 'documents'}
    <div class="space-y-3">
      <input type="file" accept=".txt,.pdf,.docx" on:change={handleFileChange} class="block" />
      {#if fileContent}
        <div class="border p-2 rounded bg-gray-50 dark:bg-gray-900 whitespace-pre-wrap max-h-40 overflow-y-auto text-sm">
          {fileContent}
        </div>
      {/if}
      <textarea
        bind:value={observations}
        placeholder={$i18n.t('Observations')}
        class="w-full p-2 border rounded dark:bg-gray-900"
        rows="3"
      ></textarea>
      <button class="bg-blue-600 text-white px-4 py-2 rounded" on:click={submitDocument}>
        {$i18n.t('Confirm')}
      </button>
    </div>
  {:else}
    <div class="flex flex-col h-full">
      <div class="flex-1 overflow-y-auto border p-2 space-y-2 rounded">
        {#each messages as m, index}
          <div class="{m.role === 'user' ? 'text-right' : 'text-left'}">
            <div class="inline-block p-2 rounded {m.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-800'}">
              {m.content}
            </div>
            {#if m.role === 'assistant' && index === messages.length - 1}
              <button class="ml-2 text-xs text-blue-600" on:click={openSaveDialog}>
                {$i18n.t('Save to Vector')}
              </button>
            {/if}
          </div>
        {/each}
      </div>
      <div class="mt-2 flex">
        <input
          type="text"
          bind:value={question}
          placeholder={$i18n.t('Your question')}
          class="flex-1 border rounded-l px-2 dark:bg-gray-900"
        />
        <button class="bg-blue-500 text-white px-4 rounded-r" on:click={sendMessage}>
          {$i18n.t('Ask')}
        </button>
      </div>
    </div>
  {/if}
</div>

<ConfirmDialog
  bind:show={showSaveDialog}
  title={$i18n.t('Save to Vector')}
  input={true}
  inputValue={saveContext}
  on:confirm={saveToVector}
  on:cancel={() => (showSaveDialog = false)}
/>
