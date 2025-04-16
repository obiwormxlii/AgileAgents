<script lang="ts">
	import MdComonent from './MdComonent.svelte';
	import { Input } from '$lib/components/ui/input';
	import { Button } from '$lib/components/ui/button';
	import * as Select from '$lib/components/ui/select';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import { Textarea } from '$lib/components/ui/textarea';
	import { invalidateAll } from '$app/navigation';
	import { enhance } from '$app/forms';

	let { data } = $props();
	let current_agent = $state('Business Analyst');

	function downloadMarkdown(markdownContent, filename) {
		const blob = new Blob([markdownContent], { type: 'text/markdown' });
		const url = URL.createObjectURL(blob);

		if (filename.endsWith('.md')) {
			filename = filename.slice(0, -3);
		}
		const a = document.createElement('a');
		a.href = url;
		a.download = filename + '.md';
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);

		URL.revokeObjectURL(url);
	}

	async function roundRobin() {
		for (const agent of data.agents) {
			const agent_name = agent.agent_name;
			await fetch(`http://localhost:8000/ai`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					project_id: data.project_id,
					agent_name: agent_name
				})
			});
			await invalidateAll();
		}
	}
</script>

{#snippet chat(message)}
	<div class="max-w-3/4 flex w-full gap-2">
		{#if message.author === 'User'}
			<div class="flex-1" />
		{/if}
		<div
			class="rounded-lg border-2 p-2 {message.author === 'User'
				? 'bg-blue-200 text-right'
				: 'bg-green-200'}"
		>
			<div>
				<b>{message.author}: </b>
				{message.message}
			</div>
		</div>
		{#if message.author !== 'User'}
			<div class="flex-1" />
		{/if}
		<form method="POST" action="?/deleteMessage" use:enhance>
			<Button type="submit" name="message_id" value={message.id}>Delete</Button>
		</form>
	</div>
{/snippet}

<h1>Test</h1>
<div class="h-sceen m-auto flex w-1/2 flex-col gap-4 p-4">
	<ScrollArea class="h-96 w-full">
		<div class="flex flex-col gap-2">
			{#each data.chats as message}
				{@render chat(message)}
			{/each}
		</div>
	</ScrollArea>

	<form method="POST" action="?/addMessage">
		<div class="flex gap-2">
			<Select.Root
				type="single"
				name="agent"
				bind:value={current_agent}
				onValueChange={(value) => (current_agent = value)}
			>
				<Select.Trigger class="w-[180px]">{current_agent}</Select.Trigger>
				<Select.Content>
					{#each data.agents as agent}
						<Select.Item value={agent.agent_name} class="bg-light">{agent.agent_name}</Select.Item>
					{/each}
				</Select.Content>
			</Select.Root>
			<Textarea name="message" class="w-full" />
			<Button type="submit">Send</Button>
		</div>
	</form>
	<form method="POST" action="?/roundRobin" use:enhance>
		<input type="hidden" name="project_id" value={data.project_id} />
		<Button type="submit">Round Robin</Button>
	</form>
</div>

<div class="m-auto flex flex-wrap gap-4 p-4">
	{#each data.docs as doc}
		<div class="flex h-96 w-96 flex-col border-2 p-8">
			<ScrollArea class="h-full w-full ">
				<div class="flex flex-wrap justify-between">
					<h2 class="text-2xl">{doc.name}</h2>
				</div>
				<MdComonent md={doc.text} />
			</ScrollArea>
			<div class="flex justify-between">
				<Button onclick={() => downloadMarkdown(doc.text, doc.name)}>Download</Button>
				<form method="POST" action="?/deleteDoc" use:enhance>
					<Button variant="destructive" type="submit" name="doc_id" value={doc.id}>Delete</Button>
				</form>
			</div>
		</div>
	{/each}
</div>
