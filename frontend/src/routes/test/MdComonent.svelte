<script>
  import SvelteMarkdown from 'svelte-markdown';

  let { md } = $props();
</script>

<SvelteMarkdown source={md} />
