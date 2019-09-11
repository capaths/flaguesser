<template>
    <v-layout align-end>
        <v-list dense width="100%" max-height="100%" id="chatList">
            <ChatMessage
                    v-for="(value, name, index) in msgs[selectedRoom]['messages']"
                    :sender="value.sender"
                    :content="value.content"
                    :key="index"
            ></ChatMessage>
            <v-textarea
                    v-model="message"
                    auto-grow
                    rows="1"
                    placeholder="Insert message here..."
                    ma-2
                    filled
                    full-width
                    row-height="30"
                    @keydown.enter.prevent="sendMessage"
            ></v-textarea>
            <v-select
                    :items="rooms"
                    placeholder="Select room..."
                    v-model="selectedRoom"
            ></v-select>
            <v-btn
                    @click.prevent="showJoinModal"
                    md-4
            >
                Join Room
            </v-btn>
            <v-btn
                    @click.prevent="showCreateModal"
                    md-4
            >
                Create Room
            </v-btn>
            <v-btn
                    @click.prevent="getCode"
                    md-4
            >
                Get Code
            </v-btn>
        </v-list>
        <v-dialog
                v-model="dialog"
                width="500"
        >
            <v-card>
                <v-card-title
                        class="headline grey lighten-2"
                        primary-title
                >
                    {{createMode ? "Create" : "Join"}} Room
                </v-card-title>

                <v-card-text>
                    <v-text-field :label="createMode ? 'Room Name':'Room Code'" v-model="roomCode">
                    </v-text-field>
                </v-card-text>

                <v-divider></v-divider>

                <v-card-actions>
                    <div class="flex-grow-1"></div>
                    <v-btn
                            color="primary"
                            text
                            @click="createMode ? createRoom() : joinRoom()"
                    >
                        {{createMode ? "Create" : "Join"}}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
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
                msgs: {
                    Global: {
                        name: 'Global',
                        messages: [],
                    },
                },
                dialog: false,
                selectedRoom: 'Global',
                roomCode: '',
                createMode: false,
                rooms: [
                    'Global',
                ],
            };
        },
        components: {
            ChatMessage,
        },
        mounted() {
            this.$options.sockets.onmessage = (message) => {
                const data = JSON.parse(message.data);
                if (data.type === 'event') {
                    if (data.event === 'new_message') {
                        this.pushMessage(data.data, data.data.room_code);
                    } else if (data.event === 'room_data') {
                        this.subscribeRoom(data.data.room.name, data.data.room.code);
                    }
                }
            };

            this.$options.sockets.onopen = () => {
                this.$socket.sendObj({
                    method: 'subscribe_chat',
                    data: {
                        username: this.user.username,
                    },
                });
            };
        },
        computed: {
            ...mapState('account', ['user']),
        },
        methods: {
            sendMessage() {
                if (this.message === '') {
                    return;
                }
                this.$socket.sendObj({
                    method: 'process_message',
                    data: {
                        content: this.message,
                        room_code: this.selectedRoom === 'Global' ? undefined : this.selectedRoom,
                    },
                });
                this.message = '';
            },
            pushMessage(message, room) {
                if (room === null) {
                    this.msgs.Global.messages.push(message);
                } else {
                    this.msgs[room].messages.push(message);
                }
                this.$forceUpdate();
            },
            showJoinModal() {
                this.createMode = false;
                this.dialog = true;
            },
            showCreateModal() {
                this.createMode = true;
                this.dialog = true;
            },
            joinRoom() {
                this.dialog = false;
                const res = this.roomCode.split(';');
                this.subscribeRoom(res[0], res[1]);

                this.roomCode = '';
            },
            getCode() {
                this.message = this.msgs[this.selectedRoom].name + ';' + this.selectedRoom;
            },
            createRoom() {
                this.dialog = false;
                this.$socket.sendObj({
                    method: 'create_room',
                    data: {
                        room_name: this.roomCode,
                    },
                });

                this.roomCode = '';
            },
            subscribeRoom(roomName, roomCode) {
                this.$socket.sendObj({
                    method: 'subscribe_room',
                    data: {
                        room_code: roomCode,
                    },
                });
                this.selectedRoom = roomCode;
                this.msgs[roomCode] = {
                    name: roomName,
                    messages: [],
                };
                this.rooms.push(roomCode);
            },
        },
    };
</script>

<style scoped>
    #chatList {
        overflow-y: scroll;
    }
</style>