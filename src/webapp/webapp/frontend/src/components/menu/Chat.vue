<template>
    <v-layout align-end>
        <v-list dense width="100%" max-height="100%" id="chatList">
            <ChatMessage
                    v-for="(value, name, index) in msgs"
                    :sender="value.sender"
                    :content="value.content"
                    :key="index"
            ></ChatMessage>
            <v-textarea
                    v-model="message"
                    auto-grow
                    rows="1"
                    ma-2
                    filled
                    full-width
                    row-height="30"
                    @keydown.enter.prevent="sendMessage"
            ></v-textarea>
        </v-list>
    </v-layout>
</template>

<script>
    import ChatMessage from './ChatMessage';
    import {mapState} from 'vuex';

    export default {
        name: 'Chat',
        data() {
            return {
                message: '',
                msgs: [],
            };
        },
        components: {
            ChatMessage,
        },
        mounted() {
            this.$options.sockets.onmessage = (message) => {
                console.log(message.data);
                if (message.data.type === 'event')
                {
                    console.log(message.data.event);
                    if (message.data.event === 'new_message')
                    {
                        this.msgs.push(message.data.data);
                    }
                }
            };
            this.$options.sockets.onopen = () => {
                this.$socket.sendObj({
                    method: 'subscribe_chat',
                    data: {},
                });
            }
        },
        computed: {
            ...mapState('account', ['user']),
        },
        methods: {
            sendMessage() {
                if (this.message === '') return;
                this.$socket.sendObj({
                    method: 'process_message',
                    data: {
                        sender: this.user.username,
                        content: this.message,
                    },
                });
                this.message = '';
            },
        },
    };
</script>

<style scoped>
    #chatList {
        overflow-y: scroll;
    }
</style>