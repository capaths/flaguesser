<template>
    <v-card width="100%" flat tile class="mx-auto">
        <v-card-title pa-0 class="pa-1 overline">{{sender}}</v-card-title>
        <v-card-text class="pa-1 body-2">{{content}}</v-card-text>
    </v-card>
</template>

<script>
    export default {
        name: 'ChatMessage',
        props: [
            'sender',
            'content',
        ],
    };
</script>
