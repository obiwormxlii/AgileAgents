import type { PageServerLoad, Actions } from './$types';

export const load: PageServerLoad = async () => {
	return {
		chats: await fetch('http://localhost:8000/messages').then((res) => res.json()),
		agents: await fetch('http://localhost:8000/agents').then((res) => res.json()),
		project_id: 1,
		docs: await fetch('http://localhost:8000/projects/1/documents').then((res) => res.json())
	};
};

export const actions: Actions = {
	addMessage: async ({ request }) => {
		const data = await request.formData();

		const project_id = 1;
		const message = data.get('message');
		const agent_name = data.get('agent');

		const body = { message: message, project_id: project_id, author: 'User' };
		console.log(JSON.stringify(body));
		await fetch('http://localhost:8000/messages', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(body)
		});

		await fetch('http://localhost:8000/ai', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				project_id: project_id,
				agent_name: agent_name
			})
		});
	},
	deleteMessage: async ({ request }) => {
		const data = await request.formData();
		const message_id = data.get('message_id');
		await fetch(`http://localhost:8000/messages/${message_id}`, {
			method: 'DELETE'
		});
	},
	deleteDoc: async ({ request }) => {
		const data = await request.formData();
		const doc_id = data.get('doc_id');
		await fetch(`http://localhost:8000/documents/${doc_id}`, {
			method: 'DELETE'
		});
	},
	roundRobin: async ({ request }) => {
		const data = await request.formData();
		const project_id = data.get('project_id');
		const agents = await fetch('http://localhost:8000/agents').then((res) => res.json());

		for (const agent of agents) {
			await fetch('http://localhost:8000/ai', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					project_id: project_id,
					agent_name: agent.agent_name
				})
			});
		}
	}
};
