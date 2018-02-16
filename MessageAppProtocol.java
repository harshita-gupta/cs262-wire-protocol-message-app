package edu.harvard.cs262.atm;

/**
 * ATM Protocol constants.
 * <p>
 * A protocol message is constructed as follows:
 * <ul>
 * <li>A header, consisting of
 * <ul>
 * <li>(byte) protocol version number
 * <li>(int) payload length, not including this field, the version field, or the
 * opcode
 * <li>(byte) operation code
 * </ul>
 * <li>optionally, additional payload, specified for each opcode
 * </ul>
 * <p>
 * If the additional payload includes a {@code String}, it will be encoded as
 * follows:
 * <ul>
 * <li>(short) number of bytes
 * <li>(byte[]) String encoded in the UTF-8 character set
 *
 * </ul>
 * <p>
 * The {@code protocol version} will be checked by the server to ensure that the
 * client and server are using the same protocol or versions of the protocol
 * that are compatible. If the server determines that the protocol version used
 * by the client and the protocol version or versions required by the server are
 * not compatible, the server will disconnect the client. In cases where the
 * protocols being used are not compatible, no other communication between the
 * client and the server is guaranteed to be understood.
 * <p>
 * The total length of a message must not be greater than 1024 bytes; given the
 * header information this means that the payload of a message cannot be greater
 * than 1018 bytes. This limits the size of the error strings that are sent
 * back to the client as well as the size of the messages sent. This
 * also means that the buffers that are allocated for the sending and receiving
 * of messages can be kept to a more reasonable size.
 * <p>
 * We follow the Java language definitions of the basic data types. In
 * particular, a {@code byte} is defined as 8 bits, and an {@code int} is defined
 * as 4 bytes (32 bits). {@code String} representations will vary from
 * environment to environment, which is why we define UTF-8 as the transfer
 * encoding for strings. Behavior not specified in this document is left as an
 * implementation decision for the particular client and server.
 */
public class MessageAppProtocol {

    /**
     * This class should not be instantiated.
     */
    protected MessageAppProtocol() {
        throw new UnsupportedOperationException();
    }

    /**
     * The maximum length of a protocol message: {@value #MAX_MESSAGE_LENGTH}
     * bytes.
     */
    public static final int MAX_MESSAGE_LENGTH = 1024;

    public static final int HEADER_SIZE = 6;

    /**
     * The maximum payload length: {@value #MAX_PAYLOAD_LENGTH} bytes.
     */
    public static final int MAX_PAYLOAD_LENGTH = MAX_MESSAGE_LENGTH
            - HEADER_SIZE;

    /** The version number, currently {@code 0x01}. */
    public static final byte VERSION = 0x01;

    /**
     * Account creation request from a client to a server. This message should
     * only be sent to a server; if received by a client it should be ignored. <br>
     * Opcode: {@code 0x10} <br>
     * Payload:
     * <ul>
     * <li>(String) username
     * </ul>
     *
     * <p>
     * The {@code username} must only contain alphanumeric characters.
     * Usernames are case-sensitive.
     * After the server processes the creation
     * request, the server sends one of the following acknowledgments to the
     * client:
     * <ul>
     * <li> {@link #CREATE_SUCCESS}, if account creation succeeds.
     * <li> {@link #CREATE_FAILURE}, if account creation fails.
     * </ul>
     */
    public static final byte CREATE_REQUEST = 0x10;

    /**
     * Account creation success. Server response to a client's
     * {@link #CREATE_REQUEST}. <br>
     * Opcode: {@code 0x11} <br>
     * Payload:
     * <ul>
     * <li>(int) username
     * </ul>
     * The {@code account_number} is the username the server just created.
     */
    public static final byte CREATE_SUCCESS = 0x11;

    /**
     * Account creation failure. Server response to a client's
     * {@link #CREATE_REQUEST}. <br>
     * Opcode: {@code 0x12} <br>
     * Payload:
     * <ul>
     * <li>(String) reason
     * </ul>
     * This message indicates that the server rejects the
     * {@link #CREATE_REQUEST} for some reason, for example:
     * <ul>
     * <li> invalid desired username (not alphanumeric)
     * <li> unavailable desired username
     * </ul>
     *
     */
    public static final byte CREATE_FAILURE = 0x12;

    /**
     * Account destruction request from a client to a server. This message
     * should only be sent to a server; if received by a client it should be
     * ignored. <br>
     * Opcode: {@code 0x20} <br>
     * Payload:
     * <ul>
     * <li>(String) username
     * </ul>
     *
     * <p>
     * The {@code account_number} is the number of the account to be deleted.
     * After the server processes the deletion request, the server sends one of
     * the following acknowledgments to the client:
     * <ul>
     * <li> {@link #DELETE_SUCCESS}, if account deletion succeeds.
     * <li>{@link #DELETE_FAILURE}, if account deletion fails.
     * </ul>
     */
    public static final byte DELETE_REQUEST = 0x20;

    /**
     * Account deletion success. Server response to a client's
     * {@link #DELETE_REQUEST}. <br>
     * Opcode: {@code 0x21} <br>
     * Payload: none
     */
    public static final byte DELETE_SUCCESS = 0x21;

    /**
     * Account deletion failure. Server response to a client's
     * {@link #DELETE_REQUEST}. <br>
     * Opcode: {@code 0x22} <br>
     * Payload:
     * <ul>
     * <li>(String) reason
     * </ul>
     * This message indicates that the server rejects the
     * {@link #DELETE_REQUEST} for some reason, for example:
     * <ul>
     * <li> invalid username (account might've already been deleted)
     * <li> message delivery to that user is pending
     * </ul>
     */
    public static final byte DELETE_FAILURE = 0x22;

    /**
     * Send message request from a client to a server. This message should
     * only be sent to a server; if received by a client it should be ignored. <br>
     * Opcode: {@code 0x30} <br>
     * Payload:
     * <ul>
     * <li>(String) sending_user
     * <li>(String) receiving_user
     * <li>(String) message
     * </ul>
     *
     * <p>
     * The {@code receiving_user} is the username of the user that should
     * receive the message. The {@code sending_user} is the user that is sending the message.
     * The {@code message} should be the content of the message.
     * After the server processes the message request, the server sends one of the following
     * acknowledgments to the client:
     * <ul>
     * <li> {@link #SEND_MESSAGE_SUCCESS}, if message sending succeeds.
     * <li>{@link #SEND_MESSAGE_FAILURE}, if message sending fails.
     * </ul>
     */
    public static final byte SEND_MESSAGE_REQUEST = 0x30;

    /**
     * Send message success. Server response to a client's {@link #SEND_MESSAGE_REQUEST}. <br>
     * Opcode: {@code 0x31} <br>
     * Payload:
     * <ul>
     * <li>(String) receiving_user
     * </ul>
     *
     * The {@code receiving_user} returned reflects the user who received the request.
     */
    public static final byte SEND_MESSAGE_SUCCESS = 0x31;

    /**
     * Send message failure. Server response to a client's {@link #SEND_MESSAGE_REQUEST}. <br>
     * Opcode: {@code 0x32} <br>
     * Payload:
     * <ul>
     * <li>(String) reason
     * </ul>
     * This message indicates that the server rejects the
     * {@link #SEND_MESSAGE_REQUEST} for some reason, for example:
     * <ul>
     * <li>invalid sending user (might have been deleted from another client)
     * <li>invalid receiving user (might have been deleted after users were last listed, by another client)
     * </ul>
     *
     */
    public static final byte SEND_MESSAGE_FAILURE = 0x32;

    /**
     * Deliver message request from a server to a client. This message should
     * only be sent to a client; if received by a server it should be ignored. <br>
     * Opcode: {@code 0x80} <br>
     * Payload:
     * <ul>
     * <li>(String) sending_user
     * <li>(String) receiving_user
     * <li>(String) message
     * </ul>
     *
     * <p>
     * The {@code receiving_user} is the username of the user that should
     * receive the message. The {@code sending_user} is the user that is sending the message.
     * The {@code message} should be the content of the message.
     * After the server processes the message request, the server sends one of the following
     * acknowledgments to the client:
     * <ul>
     * <li> {@link #DELIVER_MESSAGE_SUCCESS}, if message sending succeeds.
     * <li>{@link #DELIVER_MESSAGE_FAILURE}, if message sending fails.
     * </ul>
     */
    public static final byte DELIVER_MESSAGE_REQUEST = 0x80;

    /**
     * Send message success. Client response to a server's {@link #DELIVER_MESSAGE_REQUEST}. <br>
     * Opcode: {@code 0x81} <br>
     * Payload:
     * <ul>
     * <li>(String) receiving_user
     * </ul>
     *
     * The {@code receiving_user} returned reflects the user who received the request.
     */
    public static final byte DELIVER_MESSAGE_SUCCESS = 0x81;

    /**
     * Send message failure. Client response to a server's {@link #DELIVER_MESSAGE_REQUEST}. <br>
     * Opcode: {@code 0x82} <br>
     * Payload:
     * <ul>
     * <li>(String) reason
     * </ul>
     * This message indicates that the client rejects the
     * {@link #DELIVER_MESSAGE_REQUEST} for some reason, for example:
     * <ul>
     * <li> User that the message was intended for is not the one currently logged in.
     * </ul>
     *
     */
    public static final byte DELIVER_MESSAGE_FAILURE = 0x82;

    // /**
    //  * Withdrawal request from a client to a server. This message should only be
    //  * sent to a server; if received by a client it should be ignored. <br>
    //  * Opcode: {@code 0x40} <br>
    //  * Payload:
    //  * <ul>
    //  * <li>(int) account_number
    //  * <li>(int) amount
    //  * </ul>
    //  *
    //  * <p>
    //  * The {@code account_number} is the number of the account from which the
    //  * money should be withdrawn. The {@code amount} should be a positive
    //  * whole-number amount of USD to be withdrawn the specified account not to
    //  * exceed the account's current balance. After the server processes the
    //  * withdrawal request, the server sends one of the following acknowledgments
    //  * to the client:
    //  * <ul>
    //  * <li> {@link #WITHDRAW_SUCCESS}, if account withdrawal succeeds.
    //  * <li>{@link #WITHDRAW_FAILURE}, if account withdrawal fails.
    //  * </ul>
    //  */
    // public static final byte WITHDRAW_REQUEST = 0x40;

    // /**
    //  * Withdrawal success. Server response to a client's {@link #WITHDRAW_REQUEST}. <br>
    //  * Opcode: {@code 0x41} <br>
    //  * Payload:
    //  * <ul>
    //  * <li>(int) balance
    //  * </ul>
    //  *
    //  * The {@code balance} returned reflects the balance in the specified
    //  * account after {@code amount} is deposited.
    //  */
    // public static final byte WITHDRAW_SUCCESS = 0x41;

    // /**
    //  * Withdrawal failure. Server response to a client's {@link #WITHDRAW_REQUEST}. <br>
    //  * Opcode: {@code 0x42} <br>
    //  * Payload:
    //  * <ul>
    //  * <li>(String) reason
    //  * </ul>
    //  * This message indicates that the server rejects the
    //  * {@link #WITHDRAW_REQUEST} for some reason, for example:
    //  * <ul>
    //  * <li>invalid username,
    //  * <li>insufficient funds,
    //  * <li>invalid deposit amount.
    //  * </ul>
    //  */
    // public static final byte WITHDRAW_FAILURE = 0x42;

    /**
     * List users request from a client to a server.
     * This message should only be sent to a server; if
     * received by a client it should be ignored. <br>
     * Opcode: {@code 0x50} <br>
     * No payload.
     *
     * <p>
     * After the server processes the account balance check
     * request, the server sends one of the following acknowledgments to the
     * client:
     * <ul>
     * <li> {@link #LIST_USERS_SUCCESS}, if users list requests succeeds.
     * <li>{@link #LIST_USERS_FAILURE}, if users list requests fails.
     * </ul>
     */
    public static final byte LIST_USERS_REQUEST = 0x50;

    /**
     * List users success. Server response to a client's
     * {@link #LIST_USERS_REQUEST}. <br>
     * Opcode: {@code 0x51} <br>
     * Payload:
     * <ul>
     * <li> (String) all_users
     * </ul>
     *  <p>
     * {@code all_users} is a new-line separated list of all users currently
     * registered (who have not been deleted).
     */
    public static final byte LIST_USERS_SUCCESS = 0x51;

    // /** IMPOSSIBLE SO REMOVED
    //  * List users failure. Server response to a client's {@link #LIST_USERS_REQUEST}. <br>
    //  * Opcode: {@code 0x52} <br>
    //  * Payload:
    //  * <ul>
    //  * <li>(String) reason
    //  * </ul>
    //  * This message indicates that the server rejects the
    //  * {@link #LIST_USERS_REQUEST} for some reason, for example:
    //  * <ul>
    //  * <li> no users exist.
    //  * </ul>
    //  */
    // public static final byte LIST_USERS_FAILURE = 0x52;

    /**
     * Request from a client to a server to disconnect that the user is logging out.
     * This message should only be sent to a server; if received by a client it
     * should be ignored. <br>
     * Opcode: {@code 0x60} <br>
     * Payload: none
     *
     * <p>
     * This operation cannot fail, as it simply notifies the server of the ATM's
     * intent to shut down. (There might be cases where the bank wants to keep
     * the ATM up and running, though we omit them in this protocol). After the
     * server processes the disconnect request, the server sends
     * {@link #LOG_OUT_SUCCESS} to the client.
     */
    public static final byte LOG_OUT = 0x60;

    /**
     * End session success. Server response to a client's {@link #LOG_OUT}. <br>
     * Opcode: {@code 0x61} <br>
     * Payload: None.
     */
    public static final byte LOG_OUT_SUCCESS = 0x61;

    /**
     * Message from the server to the client indicating that a message with an
     * unknown opcode has been received. On the second receipt of an unknown
     * opcode, the server will disconnect the client, after sending an
     * {@link #LOG_OUT_SUCCESS} message. Opcode: {@code Ox62}<br>
     * Payload: None.
     */
    public static final byte UNKNOWN_OPCODE = 0x62;

     /**
     * Notification from a client to a server that a user wishes to log in.
     * This message should only be sent to a server; if received by a client it
     * should be ignored. <br>
     * Opcode: {@code 0x70} <br>
     * Payload:
     * <ul>
     * <li> (String) username
     * <p>
     * After the server processes the log in request
     * the server sends one of the following acknowledgments to the
     * client:
     * <ul>
     * <li> {@link #LOG_IN_SUCCESS}, if log in succeeds.
     * <li> {@link #LOG_IN_FAILURE}, if log in fails.
     * </ul>
     * <p>
     */
    public static final byte LOG_IN = 0x70;

    /**
     * Log in success. Server response to a client's {@link #LOG_IN}. <br>
     * Opcode: {@code 0x71} <br>
     * Payload: None.
     */
    public static final byte LOG_IN_SUCCESS = 0x71;

    /**
     * Log in failure. Server response to a client's {@link #LOG_IN}. <br>
     * Opcode: {@code 0x72} <br>
     * Payload:
     * <ul>
     * <li>(String) reason
     * </ul>
     * This message indicates that the server rejects the
     * {@link #LOG_IN_REQUEST} for some reason, for example:
     * <ul>
     * <li> no user with the username specified exists.
     * <li> This user is already logged in on another machine.
     * </ul>
     */
    public static final byte LOG_IN_FAILURE = 0x72;
}
