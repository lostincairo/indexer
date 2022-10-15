from apibara import EventFilter, IndexerRunner, Info, NewEvents
from apibara.indexer import IndexerRunnerConfiguration
from starknet_py.utils.data_transformer import FunctionCallSerializer
from starkware.starknet.public.abi_structs import identifier_manager_from_abi


indexer_id = "lostincairo"
game_address = "0x073006b1156b9fcdf8088a43281a6f87e772b0632702bf962a9d9d6d04ed3fef"
lobby_address = "0x00b9212c1a4c2f5d5695511a72f718d62138d53809dc446ca3299718f96c3d7f"


abi_init_game = [
        {
        "data": [
            {
                "name": "game_idx_counter",
                "type": "felt"
            }
        ],
        "keys": [],
        "name": "InitGameOccured",
        "type": "event"
    },
]

init_game_decoder = FunctionCallSerializer(
    abi= abi_init_game, 
    identifier_manager=identifier_manager_from_abi(abi_init_game))

def decode_init_game_event(data):
    data = [int.from_bytes(b, "big") for b in data]
    return init_game_decoder.to_python(data)

def encode_int_as_bytes(n):
    return n.to_bytes(32, "big")




async def handle_events(info: Info, block_events: NewEvents):
    """Handle a group of events grouped by block."""
    print(f"Received events for block {block_events.block.number}")
    for event in block_events.events:
        print(decode_init_game_event(event.data))

    # events = [
    #     {"address": event.address, "data": event.data, "name": event.name}
    #     for event in block_events.events
    # ]

    events = [
        decode_init_game_event(event.data)
        for event in block_events.events
    ]

    # Insert multiple documents in one call.
    await info.storage.insert_many("events", events)


async def run_indexer(server_url=None, mongo_url=None, restart=None):
    print("Starting Apibara indexer")

    runner = IndexerRunner(
        config=IndexerRunnerConfiguration(
            apibara_url=server_url,
            apibara_ssl=True,
            storage_url=mongo_url,
        ),
        reset_state=restart,
        indexer_id=indexer_id,
        new_events_handler=handle_events,
    )


    runner.add_event_filters(
        filters=[
            # EventFilter.from_event_name(
            #     name="AskToQueueOccured",
            #     address=lobby_address,
            # ),
            EventFilter.from_event_name(
                name="InitGameOccured",
                address=game_address,
            ),
            # EventFilter.from_event_name(
            #     name="StartGameOccured",
            #     address=game_address,
            # ),
            # EventFilter.from_event_name(
            #     name="ActivateGameOccured",
            #     address=game_address,
            # ),
            # EventFilter.from_event_name(
            #     name="InitialPositionSetOccured",
            #     address=game_address,
            # ),
            # EventFilter.from_event_name(
            #     name="InitPlayerOccured",
            #     address=game_address,
            # ),
            # EventFilter.from_event_name(
            #     name="ActionOccured",
            #     address=game_address,
            # ),
            # EventFilter.from_event_name(
            #     name="MoveOccured",
            #     address=game_address,
            # ),
            # EventFilter.from_event_name(
            #     name="EndRoundOccured",
            #     address=game_address,
            # ),
            # EventFilter.from_event_name(
            #     name="EndGameOccured",
            #     address=game_address,
            # ),
            # EventFilter.from_event_name(
            #     name="quest_progress",
            #     address=game_address,
            # ),
        ],
        index_from_block=367_160,
    )

    print("Initialization completed. Entering main loop.")

    await runner.run()
